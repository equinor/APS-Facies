import random
import socket
import string
import time
import traceback
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Union
from zipfile import ZipFile, ZIP_DEFLATED


def get_rms_information(config):
    location = Path(config.project.filename).absolute()
    machine = socket.getfqdn()
    return f'{machine}:{location}'


def dump_debug_information(config):
    print('The workflow failed. The job and the model will be written to disk')
    when = time.localtime()
    prefix = '{year}{month:02}{day:02}-{hour:02}{minute:02}{second:02}-{random}-APS'.format(
        year=when.tm_year,
        month=when.tm_mon,
        day=when.tm_mday,
        hour=when.tm_hour,
        minute=when.tm_min,
        second=when.tm_sec,
        random=''.join(random.choices(string.ascii_letters) + random.choices(string.digits, k=5)),
    )
    with ZipFile(prefix + '.zip', mode='x', compression=ZIP_DEFLATED) as zipfile:
        def dump(file_name: str, data: Union[str, bytes], encoding: str = 'UTF-8') -> None:
            path = Path(prefix) / file_name
            with zipfile.open(str(path), 'w') as f:
                if isinstance(data, str):
                    data = data.encode(encoding)
                if not data or data[-1] != b'\n':
                    data += b'\n'
                f.write(data)

        dump('model.xml', config.model)
        dump('state.json', config.to_json())
        dump('traceback.txt', traceback.format_exc())
        dump('where.txt', get_rms_information(config))


class State(Enum):
    READ = auto()
    HEADER = auto()
    PARAMETER = auto()


def parse_dot_master(path):
    header = {}
    parameters = []
    state = None
    with open(path) as file:
        parameter_index = 0
        for line in file:
            line = line.strip()
            if line == 'Begin GEOMATIC file header':
                state = State.HEADER
                continue
            elif line == 'End GEOMATIC file header':
                state = State.READ

            elif line == 'Begin parameter':
                state = State.PARAMETER
                if len(parameters) == parameter_index:
                    parameters.append({})
                continue
            elif line == 'End parameter':
                state = State.READ
                parameter_index += 1

            if state == State.READ:
                continue
            elif state == State.HEADER:
                key, value = _split(line)
                header[key] = value
            elif state == State.PARAMETER:
                try:
                    name, value = _split(line)
                except ValueError:
                    # The (presumable) JSON contains '='. Likely as part of a base64 encoded value
                    name, *value = _split(line)
                    value = '='.join(value)
                parameters[parameter_index][name] = _parse(value)
    return {
        'header': header,
        'parameters': parameters,
    }


def _split(line: str, sep: str = ' ='):
    return tuple(item.strip() for item in line.split(sep))


def _parse(value: str):
    try:
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S:%f')
    except ValueError:
        try:
            return float(value)
        except ValueError:
            try:
                return int(value)
            except ValueError:
                if value.upper() in ['FALSE', 'TRUE']:
                    return value.upper() == 'TRUE'
                else:
                    return value
