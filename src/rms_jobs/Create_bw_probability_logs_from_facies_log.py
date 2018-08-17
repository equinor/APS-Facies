#!/bin/env python
# -*- coding: utf-8 -*-
from src.utils.roxar.modifyBlockedWellData import createProbabilityLogs
from src.utils.methods import get_run_parameters


def run(roxar=None, project=None, **kwargs):
    params = get_run_parameters(**kwargs)

    createProbabilityLogs(
        project,
        grid_model_name=params['grid_model_name'],
        bw_name=params['blocked_wells_set_name'],
        facies_log_name=params['facies_log_name'],
        additional_unobserved_facies_list=params['additional_unobserved_facies_list'],
        prefix_prob_logs=params['prefix_prob_logs'],
    )


if __name__ == '__main__':
    import roxar
    run(roxar, project)
