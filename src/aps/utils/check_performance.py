#!/bin/env python
# -*- coding: utf-8 -*-

import cProfile


def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats(sort='time')

    return profiled_func


def get_number():
    yield from range(5000000)


@do_cprofile
def function_to_profile():
    sum_of_y = 0.0
    for x in get_number():
        y = math.sqrt(x)
        sum_of_y += y
    return sum_of_y


# --------------- Test script ------------------------------------------
if __name__ == '__main__':
    import math

    # perform profiling
    print(function_to_profile())
