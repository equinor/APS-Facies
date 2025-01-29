# -*- coding: utf-8 -*-
import pytest

from aps.algorithms.properties import FmuProperty
from aps.algorithms.trend import Point3DProperty


test_data = [
    ((1, 1, 1), (1, 1, 1), (False, False, False)),
    (((1, 1, 1),), (1, 1, 1), (False, False, False)),
    ([2, 3, 4], (2, 3, 4), (False, False, False)),
    (((0, 0, 0), (True, True, True)), (0, 0, 0), (True, True, True)),
    (([1, 2, 3], [True, False, True]), (1, 2, 3), (True, False, True)),
    # Instance of Point3DProperty
    ((Point3DProperty((0, 0, 0)),), (0, 0, 0), (False, False, False)),
    (Point3DProperty((0, 0, 0)), (0, 0, 0), (False, False, False)),
    (
        (
            FmuProperty(0, False),
            FmuProperty(1, True),
            FmuProperty(3, True),
        ),
        (0, 1, 3),
        (False, True, True),
    ),
]


@pytest.mark.parametrize('input_args,expected_origin,expected_fmu', test_data)
def test_creation_point_3d_property(input_args, expected_origin, expected_fmu):
    actual = Point3DProperty(*input_args)
    assert expected_origin == actual.as_point()
    assert expected_fmu == actual.fmu_as_point()
