# -*- coding: utf-8 -*-
import pytest

from src.utils.parsing import parse_signature


testdata = [
    ('ui.call("get_grid_models")', ('get_grid_models', [])),
    ('ui.call("get_zones", "GridModel1", undefined)', ('get_zones', ["GridModel1", None])),
]


@pytest.mark.parametrize('signature,expected', testdata)
def test_parse_signature(signature, expected):
    method, arguments = parse_signature(signature)
    assert (method, arguments) == expected
