import random
import string
import time
import traceback
from pathlib import Path
from typing import Union
from zipfile import ZipFile, ZIP_DEFLATED


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
