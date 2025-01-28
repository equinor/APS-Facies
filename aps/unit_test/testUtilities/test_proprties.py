# -*- coding: utf-8 -*-
import pytest

from aps.algorithms.properties import is_between

test_data = [
    (0.5, 0, 1, False, False, True),
    (5, 0, 1, False, False, False),
    (0, 0, 1, False, False, True),
    (0, 0, 1, False, True, False),
    (1, 0, 1, True, False, False),
    (1, 0, 1, True, True, False),
]


@pytest.mark.parametrize(
    'value,_min,_max,strictly_less,strictly_greater,expected', test_data
)
def test_is_between(value, _min, _max, strictly_less, strictly_greater, expected):
    actual = is_between(value, _min, _max, strictly_less, strictly_greater)
    assert expected == actual
