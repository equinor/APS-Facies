#!/bin/env python
# -*- coding: utf-8 -*-
import os

def get_text_value(input_dict: dict, parent_kw: str, kw: str, default: str=None)-> str:
    value = input_dict[kw] if kw in input_dict else None
    if value is None:
        if default is not None:
            return default
        raise ValueError(f"Missing keyword '{kw}' under keyword '{parent_kw}' ")
    return str(value)

def get_int_value(input_dict: dict, parent_kw: str, kw: str)-> int:
    value = input_dict[kw] if kw in input_dict else None
    if value is None:
        raise ValueError(f"Missing keyword '{kw}' under keyword '{parent_kw}' ")
    return value

def get_float_value(input_dict: dict, parent_kw: str, kw: str)-> float:
    value = input_dict[kw] if kw in input_dict else None
    if value is None:
        raise ValueError(f"Missing keyword '{kw}' under keyword '{parent_kw}' ")
    return value

def get_bool_value(input_dict: dict, kw: str, default_value: bool = False)-> bool:
    value = input_dict[kw] if kw in input_dict else None
    if value is None:
        return default_value
    return value

def get_dict(input_dict: dict, parent_kw: str = None, kw: str = None)-> dict:
    value = input_dict[kw] if kw in input_dict else None
    if value is None:
        raise ValueError(f"Missing keyword '{kw}' under keyword '{parent_kw}' ")
    return value

def get_list(input_dict: dict, parent_kw: str = None, kw: str = None)-> list:
    value = input_dict[kw] if kw in input_dict else None
    if value is None:
        raise ValueError(f"Missing keyword '{kw}' under keyword '{parent_kw}' ")
    return value

def readYml(file_name):
    try:
        import yaml
    except ImportError:
        raise ImportError('PyYaml is required')

    if not os.path.exists(file_name):
        raise IOError(f"File {file_name} does not exist")

    with open(file_name, 'r', encoding='utf-8') as file:
        spec_all = yaml.safe_load(file)
    return spec_all
