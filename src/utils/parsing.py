# -*- coding: utf-8 -*-
from json import loads
import re


def _sanitize_for_json(raw_parameters):
    if 'undefined' in raw_parameters:
        raw_parameters = raw_parameters.replace('undefined', 'null')
    return '[' + raw_parameters + ']'


def _get_arguments(raw):
    raw = _sanitize_for_json(raw)
    arguments = loads(raw)
    return arguments


def parse_signature(signature):
    parse = re.match(r"ui\.call\(['\"](?P<method_name>\w+)['\"](, ?)?(?P<arguments>.*)\)", signature).groupdict()
    arguments = _get_arguments(parse['arguments'])
    method_name = parse['method_name']
    return method_name, arguments
