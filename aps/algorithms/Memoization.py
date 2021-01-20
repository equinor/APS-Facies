#!/bin/env python
# -*- coding: utf-8 -*-
import numpy as np


class RoundOffConstant:
    low = 0.999999
    high = 1.000001
    shift_tolerance = 0.001


class MemoizationItem:
    __slots__ = 'cell_index_set'

    def __init__(self, cell_index=None):
        self.cell_index_set = set()
        if cell_index is not None:
            self.cell_index_set.add(cell_index)

    def add_cell_index(self, cell_index):
        if cell_index is not None:
            self.cell_index_set.add(cell_index)

    def get_cell_indices(self):
        return np.array(list(self.cell_index_set))
