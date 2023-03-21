# -*- coding: utf-8 -*-
from json import loads
import re
from typing import List, Tuple, NewType

Arguments = NewType('Arguments', List[str])


def _sanitize_for_json(raw_parameters: str) -> str:
    if 'undefined' in raw_parameters:
        raw_parameters = raw_parameters.replace('undefined', 'null')
    return f'[{raw_parameters}]'


def _get_arguments(raw: str) -> Arguments:
    raw = _sanitize_for_json(raw)
    return loads(raw)


def parse_signature(signature: str) -> Tuple[str, Arguments]:
    parse = re.match(r"(api/)?ui\.call\(['\"](?P<method_name>\w+)['\"](, ?)?(?P<arguments>.*)\)", signature).groupdict()
    arguments = _get_arguments(parse['arguments'])
    method_name = parse['method_name']
    return method_name, arguments
