# -*- coding: utf-8 -*-
import roxar
from src.utils.roxar.rms_project_data import get_grid_models


def get_grid_names():
    return [grid.name for grid in get_grid_models(project)]


def get_zones():
    pass
