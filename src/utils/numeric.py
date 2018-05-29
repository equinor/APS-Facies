# -*- coding: utf-8 -*-
def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
