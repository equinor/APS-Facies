#!/bin/env python
# -*- coding: utf-8 -*-# Calculate prob logs from original facies logs
"""
Description:
The fraction of each facies within a blocked well grid cell is used as estimate for the probability.
The script will read raw (original) well logs with facies interpretation,
create binary probability logs for each modelled facies and create upscaled probability logs
which will be defined as the fraction of each modelled facies found within each grid cell
in the blocked wells for each facies.

"""

import roxar
import roxar.jobs
import xtgeo
import sys

import numpy as np
import math
import pprint
from pathlib import Path

from aps.utils.constants.simple import Debug
from aps.utils.ymlUtils import get_text_value, get_dict, get_list, get_int_value, get_bool_value, readYml
from aps.utils.methods import check_missing_keywords_list, get_cond_prob_dict, expand_wildcards
from aps.utils.roxar.grid_model import  get_zone_layer_numbering

def run(params):
    if not sys.warnoptions:
        import warnings
        warnings.simplefilter("ignore")

    project = params['project']
    if params['model_file']:
        # Read all parameters from yml file
        params = read_model_file(params['model_file'])
        params['project'] = project

    # Check that all necessary keywords are specified
    keywords_required = [
        "project",
        "modelling_facies_per_zone",
        "prefix",
        "well_list",
        "trajectory",
        "logrun",
        "facies_log_name",
        "zone_log_name",
        "grid_model_name",
        "bw_job_list",
        "zone_param_name",
        "average_prob_log_prefix",
    ]
    check_missing_keywords_list(params, keywords_required)

    modelling_facies_per_zone_dict = params['modelling_facies_per_zone']
    well_name_list_input = params.get('well_list')
    prefix_prob_logs = params.get('prefix', 'Prob')
    trajectory = params.get('trajectory', 'Drilled trajectory')
    logrun = params.get('logrun')
    facies_log_name = params.get('facies_log_name')
    zone_log_name = params.get('zone_log_name')
    grid_model_name = params.get('grid_model_name')
    blocked_well_job_list = params.get('bw_job_list')
    blocked_well_zone_log_name = params.get('bw_zone_log_name', None)
    facies_code_mapping = params.get('facies_mapping', None)
    bias_weighting = params.get('bias_weighting', None)
    use_largest_facies_prob = params.get('use_largest_facies_prob', False)
    prob_cond_input_dict = params.get('prob_cond', None)
    eps = params.get('tolerance', 0.001)
    debug_level = params.get('debug_level', Debug.OFF)
    zone_param_name = params.get('zone_param_name')
    average_prob_log_prefix = params.get('average_prob_log_prefix')
    sim_box_thickness = params.get('sim_box_thickness',None)

    keywords_optional = [
        "bw_zone_log_name",
        "facies_mapping",
        "bias_weighting",
        "use_largest_facies_prob",
        "prob_cond",
        "tolerance",
        "debug_level",
        "sim_box_thickness",
    ]
    for key in params.keys():
        if (key not in keywords_required) and (key not in keywords_optional):
            raise KeyError(f" Unknown keyword: {key} ")

    # Get list of all wells and expand wildcard wellnames to list of well names
    full_well_list = project.wells.keys()
    if len(full_well_list) == 0:
        print("No wells found in the RMS project.")
        return

    well_name_list = list(expand_wildcards(well_name_list_input, full_well_list))
    if len(well_name_list) == 0:
        print("No wells matching specification of wells found in RMS project.")
        return

    if debug_level >= Debug.ON:
        print(f"- Wells used: ")
        for wname in well_name_list:
            print(f"-  {wname}")

    # Get the code and names dicts for both zone log and facies log
    facies_code_names_dict, zone_code_names_dict = \
        get_facies_and_zone_logs(project,
            well_name_list,
            trajectory,
            logrun,
            facies_log_name,
            zone_log_name,
            debug_level)

    if debug_level >= Debug.ON:
        print(f"- Facies and zones used when calculating probability logs:")
        for zone_number, facies_list in modelling_facies_per_zone_dict.items():
            zone_name = zone_code_names_dict[zone_number]
            print(f"-  Zone:  {zone_number}   {zone_name}   with facies:")
            for fname in facies_list:
                print(f"-    {fname}")


    # Make a dict with a key consisting of (zone_number, modelled_facies, interpreted_facies)
    # from the text string key.
    zone_number_list = modelling_facies_per_zone_dict.keys()
    prob_cond_dict = None
    if prob_cond_input_dict is not None:
        prob_cond_dict = get_cond_prob_dict(prob_cond_input_dict, zone_number_list, common_facies_list=False)
    if debug_level >= Debug.VERBOSE:
        if prob_cond_dict is not None:
            sorted_by_zone_dict = dict(sorted(prob_cond_dict.items(), key=lambda item: (item[0][0], item [0][2], item[0][1])))
            print("-- Specified conditional probabilities for modelled facies given interpretd facies:")
            for key, prob_value in sorted_by_zone_dict.items():
                print(f'--  Zone: {key[0]}  Prob( {key[1]} | {key[2]} ) = {prob_value}')

    # Let zone log for blocked well data have the same name as original zone log if not specified
    if  not blocked_well_zone_log_name:
        blocked_well_zone_log_name = zone_log_name

    # Create probability logs for each specified wells in the original logs
    prob_log_names = prob_logs_per_facies(project,
        well_name_list,
        modelling_facies_per_zone_dict,
        facies_code_names_dict,
        zone_code_names_dict,
        prefix_prob_logs,
        trajectory,
        logrun,
        facies_log_name,
        zone_log_name,
        facies_code_mapping=facies_code_mapping,
        prob_cond=prob_cond_dict,
        eps=eps,
        debug_level=debug_level,
    )

    # Block the probability logs using arithmetic average of binary logs to get
    # blocked well probability logs representing the facies fraction in each grid cell
    for jobname in blocked_well_job_list:
        if debug_level >= Debug.ON:
            print(" ")
            print(f"- Calculate probability logs for blocked wells defined by the job: {jobname}")

        bw_name = blockwells_prob_logs(project,
            grid_model_name,
            blocked_well_zone_log_name,
            modelling_facies_per_zone_dict,
            jobname,
            prob_log_names,
            logrun,
            prefix_prob_logs,
            bias_weighting=bias_weighting,
            use_largest_facies_prob=use_largest_facies_prob,
            eps=0.05,
            debug_level=debug_level)

    # Calculate and write files with average prob logs over all wells (vpc)
    if average_prob_log_prefix:
        average_prob_logs(project,
            grid_model_name,
            bw_name,
            prob_log_names,
            well_name_list,
            zone_param_name,
            average_prob_log_prefix,
            sim_box_thickness)


def prob_logs_per_facies(project,
        well_name_list,
        modelling_facies_per_zone_dict,
        facies_code_names_dict,
        zone_code_names_dict,
        prefix_prob_logs,
        trajectory,
        logrun,
        facies_log_name,
        zone_log_name,
        facies_code_mapping=None,
        prob_cond=None,
        eps=0.001,
        debug_level=Debug.OFF,
    ):
    if len(well_name_list) == 0:
        return

    # Check use of facies_code_mapping
    if not facies_code_mapping:
        if debug_level >= Debug.ON:
            print(f"- No facies is merged together when using {facies_log_name} ")
        facies_code_mapping = facies_code_names_dict
    else:
        if debug_level >= Debug.ON:
            print(f"- Merge facies together when using {facies_log_name}")

    # Check prob_cond
    if prob_cond:
        err_msg_list =[]
        for zone_number, zone_name in zone_code_names_dict.items():
            if zone_number not in modelling_facies_per_zone_dict:
                # This is a zone number not specified to be modelled
                continue
            facies_list = modelling_facies_per_zone_dict[zone_number]
            for cond_facies in facies_list:
                sum_prob = 0
                for facies in facies_list:
                    key  = (zone_number, facies, cond_facies)
                    prob = prob_cond[key]
                    sum_prob += prob
                if math.fabs(sum_prob - 1.0) > eps:
                    err_msg = f"Sum of probabilities for facies conditioned to {cond_facies}  "
                    err_msg_list.append(err_msg)
                    err_msg = f"in zone {zone_name} with zone_number {zone_number} is {sum_prob}. Must be normalized to 1.0"
                    err_msg_list.append(err_msg)
        if len(err_msg_list) > 0:
            for msg in err_msg_list:
                print(msg)
            raise ValueError("Error in specification of conditional probabilities.")



    # Output probability log names use the facies names specified in modelling_facies_per_zone_dict input
    prob_log_names = []
    for zone_number, zone_name in zone_code_names_dict.items():
        if zone_number not in modelling_facies_per_zone_dict:
            # This is a zone number not specified to be modelled
            continue
        facies_list = modelling_facies_per_zone_dict[zone_number]
        for fname in facies_list:
            prob_log_name = prefix_prob_logs + "_" + fname
            if prob_log_name not in prob_log_names:
                prob_log_names.append(prob_log_name)

    # The main loop over all wells specified
    for well_name in well_name_list:
        if debug_level >= Debug.ON:
            print(f"- Well: {well_name} ")
        well = xtgeo.well_from_roxar(project,
            well_name,
            trajectory=trajectory,
            logrun=logrun,
            lognames='all',
            inclmd=True)

        # Clean up log set by removing empty discrete logs
        # This avoid error message when the logs are put
        # back to RMS project.
        for logname in well.lognames:
            if well.get_logtype(logname) == "DISC":
                if not well.get_logrecord(logname):
                    if debug_level >= Debug.ON:
                        print(f"- Delete empty log {logname} from well {well.name}")
                    well.delete_log(logname)

        for prob_log_name in prob_log_names:
            if debug_level >= Debug.VERBOSE:
                print(f"-- Create or update log: {prob_log_name} in well {well.name}  ")
            well.create_log(prob_log_name)

        # Validate facies code mapping
        err_msg_list =[]
        for code in facies_code_names_dict.keys():
            if code not in facies_code_mapping.keys():
                err_msg = f"Facies code {code} is not defined in facies code mapping."
                err_msg_list.append(err_msg)
                err_msg = f"Edit facies code mapping."
                err_msg_list.append(err_msg)
        if len(err_msg_list) > 0:
            err_msg = f"Facies code mapping:  {facies_code_mapping}."
            err_msg_list.append(err_msg)
            for err_msg in err_msg_list:
                print(err_msg)
            raise ValueError(f"Some facies codes found in the log {facies_log_name} is not defined in the facies code mapping.")


        # Calculate prob logs
        df_well = well.dataframe

        if not prob_cond:
            # Calculate prob logs as binary logs (prob = 0 or prob = 1)
            # For each zone the list of modelled facies may vary
            # Ensure that only the modelled facies for the zone are given any probability
            # All other facies is set to undefined. The sum of the modelled facies should be
            # normalized to 1

            for zone_number, zone_name in zone_code_names_dict.items():
                if zone_number not in modelling_facies_per_zone_dict:
                    # This is a zone number not specified to be modelled
                    continue

                facies_names_used =[]
                for code in facies_code_names_dict.keys():
                    facies_name = facies_code_mapping[code]
                    if facies_name in modelling_facies_per_zone_dict[zone_number]:
                        # Multiple facies codes can correspond to the same facies name if facies is to be merged
                        prob_log_name = prefix_prob_logs + "_" + facies_name
                        if facies_name not in facies_names_used:
                            facies_names_used.append(facies_name)

                            selected = (df_well[facies_log_name] != code) & (df_well[zone_log_name] == zone_number)
                            df_well.loc[selected , prob_log_name] = 0.0

                            selected = (df_well[facies_log_name] == code) & (df_well[zone_log_name] == zone_number)
                            df_well.loc[selected, prob_log_name] = 1.0
                            df_well.loc[np.isnan(df_well[facies_log_name]), prob_log_name] = np.nan
                        else:
                            # This is a facies name that is used by multiple original facies codes (It is a merged facies)
                            # Ensure that the probability is set to 1 for this code also.
                            selected = (df_well[facies_log_name] == code) & (df_well[zone_log_name] == zone_number)
                            df_well.loc[selected, prob_log_name] = 1.0
                    else:
                        # This is a facies not to be used as modelled facies. The probability should be undefined
                        if facies_name.upper() == "UNDEFINED":
                            continue
                        prob_log_name = prefix_prob_logs + "_" + facies_name
                        selected = (df_well[facies_log_name] == code) & (df_well[zone_log_name] == zone_number)
                        df_well.loc[selected, prob_log_name] = np.nan
        else:
            # Calculate prob logs using conditional prob
            err_msg_list =[]
            for zone_number, zone_name in zone_code_names_dict.items():
                if zone_number not in modelling_facies_per_zone_dict:
                    # This is a zone number not specified to be modelled
                    continue

                for cond_code in facies_code_names_dict.keys():
                    cond_facies = facies_code_mapping[cond_code]
                    if cond_facies.upper() == "UNDEFINED":
                        continue
                    for code in facies_code_names_dict.keys():
                        facies_name = facies_code_mapping[code]
                        if facies_name in modelling_facies_per_zone_dict[zone_number]:
                            if cond_facies in modelling_facies_per_zone_dict[zone_number]:
                                prob_log_name = prefix_prob_logs + "_" + facies_name
                                key = (zone_number, facies_name, cond_facies)
                                prob = prob_cond[key]
                                if prob < 0 or prob > 1.0:
                                    err_msg = f"Conditional probability P({facies_name}|{cond_facies}) is outside [0,1]"
                                    err_msg_list.append(err_msg)
                                else:
                                    selected = (df_well[facies_log_name] == cond_code) & (df_well[zone_log_name] == zone_number)
                                    df_well.loc[selected, prob_log_name] = prob
                                    df_well.loc[np.isnan(df_well[facies_log_name]), prob_log_name] = np.nan

            if len(err_msg_list) > 0:
                for err_msg in err_msg_list:
                    print(err_msg)
                raise ValueError('Errors in specification of conditional probabilities for modelled facies. Check specification.')

        if debug_level >= Debug.ON:
            print(f"- Update probability logs for well {well_name}  ")

        well.to_roxar(project,
            well_name,
            lognames='all',
            trajectory=trajectory,
            logrun=logrun)

    return prob_log_names


def blockwells_prob_logs(project,
        grid_model_name: str,
        blocked_well_zone_log_name: str,
        modelling_facies_per_zone_dict: dict,
        blocked_well_job_name: str,
        blocked_well_prob_log_names: list,
        log_run_name: str,
        prefix: str,
        bias_weighting: dict = None,
        use_largest_facies_prob: bool = False,
        eps: float = 0.05,
        debug_level: Debug = Debug.OFF
    ):
    bw_job = roxar.jobs.Job.get_job(owner=['Grid models', grid_model_name, 'Grid'],
            type='Block Wells',
            name=blocked_well_job_name)

    pp = pprint.PrettyPrinter()

    # Get model parameters for the BW job in RMS
    params = bw_job.get_arguments()
    if debug_level >= Debug.VERY_VERBOSE:
        print(" ")
        print(f"--- Initial values of blocked well job parameter setting:")
        pp.pprint(params)

    blocked_wells_name = params['BlockedWellsName']
    update = False
    key = 'Continuous Blocked Log'
    if key not in params:
        params[key] = []

        for bw_log_name in blocked_well_prob_log_names:
            bw_log = define_new_bw_param(bw_log_name, log_run_name)
            if debug_level >= Debug.VERBOSE:
                print(f"-- Create new blocked well parameter: {bw_log_name}  ")
            params['Continuous Blocked Log'].append(bw_log)
            update = True
    else:
        for bw_log_name in blocked_well_prob_log_names:
            found = False
            for bw_log in params['Continuous Blocked Log']:
                if bw_log_name == bw_log['Name']:
                    found = True
                    break

            if not found:
                bw_log = define_new_bw_param(bw_log_name, log_run_name)
                if debug_level >= Debug.VERBOSE:
                    print(f"-- Create new blocked well parameter: {bw_log_name}  ")
                params['Continuous Blocked Log'].append(bw_log)
                update = True


    if update:
        if debug_level >= Debug.ON:
            print(" ")
            print(f"- Update blocked well job: {blocked_well_job_name}  ")

        if debug_level >= Debug.VERY_VERBOSE:
            print(" ")
            print(f"--- Updated blocked well job parameter settings:")
            pp.pprint(params)

        check_params, err_msg_list, warn_msg_list = bw_job.check(params)
        if check_params:
            bw_job.set_arguments(params)
            if len(warn_msg_list) > 0:
                print(f"Warnings from updating block well job: {bw_job.name}  ")
                for warning_msg in warn_msg_list:
                    print(warning_msg)
        else:
            if len(warn_msg_list) > 0:
                print(f"Warnings from updating block well job: {bw_job.name}  ")
                for warning_msg in warn_msg_list:
                    print(warning_msg)
            if len(err_msg_list) > 0:
                print(f"Errors from updating block well job:  {bw_job.name} ")
                for err_msg in err_msg_list:
                    print(err_msg)
                raise ValueError(f"Some errors found when updating blocked well job parameters for  {bw_job.name}  of type {bw_job.type } ")

        bw_job.save()

    if debug_level >= Debug.ON:
        print(f"- Run well blocking job: {blocked_well_job_name} and update: {blocked_wells_name}.")
    bw_job.execute()

    # Normalization check and update the blocked wells again
    normalize_and_check(project,
        grid_model_name,
        blocked_wells_name,
        blocked_well_prob_log_names,
        blocked_well_zone_log_name,
        modelling_facies_per_zone_dict,
        prefix,
        bias_weighting,
        use_largest_facies_prob,
        eps,
        debug_level=debug_level)

    return blocked_wells_name

def define_new_bw_param(
        bw_log_name: str,
        log_run_name: str,
        debug_level: Debug = Debug.OFF
    ):
    bw_log = {}
    bw_log['Name'] = bw_log_name
    bw_log['LogRun'] = log_run_name
    bw_log['CellLayerAveraging'] = False
    bw_log['AverageMethod'] = 'ARITHMETIC'
    return bw_log


def normalize_and_check(project,
    grid_model_name: str,
    blocked_wells_name: str,
    blocked_well_prob_log_names: list,
    blocked_well_zone_log_name: str,
    modelling_facies_per_zone_dict: dict,
    prefix: str,
    bias_weighting: dict = None,
    use_largest_facies_prob: bool = False,
    eps: float = 0.05,
    debug_level: Debug = Debug.OFF):
    """
    Normalize blockedwell probability logs if necessary
    """
    if debug_level >= Debug.ON:
        print(f"- Normalize probability logs in blocked wells set {blocked_wells_name} ")
    blocked_wells = project.grid_models[grid_model_name].blocked_wells_set[blocked_wells_name]

    bias_specified = bias_weighting is not None
    if not bias_specified:
        bias_weighting ={}
        for zone_number, facies_list in modelling_facies_per_zone_dict.items():
            for fname in facies_list:
                bias_weighting[fname] = 1.0
    else:
        if debug_level >= Debug.ON:
            print("Use weight factors to create biased blocked well facies probabilities")
            pp = pprint.PrettyPrinter()
            pp.pprint(bias_weighting)

    for name in blocked_wells.get_well_names():
        if debug_level >= Debug.VERBOSE:
            print(f"-- Check and normalize prob logs in blocked well set {blocked_wells_name} and well {name}")
        lognames = blocked_well_prob_log_names.copy()
        lognames.append(blocked_well_zone_log_name)
        bw_well = xtgeo.blockedwell_from_roxar(project,
                grid_model_name,
                blocked_wells_name,
                name,
                lognames=lognames)

        df_blocked_well = bw_well.dataframe.copy()
        for zone_number, facies_list in modelling_facies_per_zone_dict.items():
            selected = (df_blocked_well[blocked_well_zone_log_name] == zone_number)
            prob_log_name = prefix + "_" + facies_list[0]
            prob_log = df_blocked_well.loc[selected, prob_log_name]
            sum_prob_log = np.zeros(len(prob_log),dtype=np.float32)
            for fname in facies_list:
                prob_log_name = prefix + "_" + fname
                prob_log = df_blocked_well.loc[selected, prob_log_name] * float(bias_weighting[fname])
                sum_prob_log = sum_prob_log + prob_log

            if not bias_specified:
                # Check if the normalization is far away from 1
                checked_cell_values = sum_prob_log[(sum_prob_log > (1+ eps)) | (sum_prob_log < (1-eps))]
                n_cells_without_normalization = len(checked_cell_values)
                if n_cells_without_normalization > 0:
                    print(f"Warning: Number of blocked well grid cells from {blocked_wells_name} for well {name} with sum "
                        f"of probabilities outside [{1-eps},{1+eps}] is:{n_cells_without_normalization} ")
                    print("Will continue with normalization.")
                    if debug_level >= Debug.ON:
                        print(f"- Values not normalized within tolerance {eps}  :")
                        print(f"{checked_cell_values} ")

            # Normalization
            prob_log_names = []
            for fname in facies_list:
                prob_log_name = prefix + "_" + fname
                prob_log_names.append(prob_log_name)
                prob_log = df_blocked_well.loc[selected, prob_log_name] * float(bias_weighting[fname])
                prob_log = prob_log/sum_prob_log
                df_blocked_well.loc[selected,prob_log_name] = prob_log

            #  Find the column with max probability per line
            if use_largest_facies_prob:
                prob_logs = df_blocked_well.loc[selected, prob_log_names]
                col_indices = prob_logs.idxmax(axis='columns')

                active_col_names = col_indices[col_indices.notna()]
                nonactive_col_names = col_indices[col_indices.isna()]

                # Initialize all values for probabilities for selected rows to nan
                df_blocked_well.loc[selected,prob_log_names] = 0

                for i in active_col_names.index:
                    df_blocked_well.loc[i,active_col_names[i]] = 1
                for i in nonactive_col_names.index:
                    df_blocked_well.loc[i,prob_log_names ] = np.nan

        # Verify normalization
        for zone_number, facies_list in modelling_facies_per_zone_dict.items():
            selected = (df_blocked_well[blocked_well_zone_log_name] == zone_number)
            prob_log_name = prefix + "_" + facies_list[0]
            prob_log = df_blocked_well.loc[selected, prob_log_name]
            sum_prob_log = np.zeros(len(prob_log),dtype=np.float32)
            for fname in facies_list:
                prob_log_name = prefix + "_" + fname
                prob_log = df_blocked_well.loc[selected, prob_log_name]
                sum_prob_log = sum_prob_log + prob_log
            checked_cell_values = sum_prob_log[(sum_prob_log > 1.001) | (sum_prob_log < 0.999)]
            n_cells_without_normalization = len(checked_cell_values)
            if n_cells_without_normalization > 0:
                print(f"Error: Number of blocked well grid cells not normalized: {n_cells_without_normalization}  ")
                print(f"Values not normalized: {checked_cell_values} ")
                raise ValueError(
                    f"Normalization error for well {name} in blocked well "
                    f"set {blocked_wells_name} for probability logs {blocked_well_prob_log_names}")

        # Set the updated blocked well data
        bw_well.dataframe = df_blocked_well
        bw_well.to_roxar(project,
            grid_model_name,
            blocked_wells_name,
            name,
            lognames='all')



def average_prob_logs(project,
        grid_model_name: str,
        bw_name: str,
        bw_prob_log_names: list,
        well_list: list,
        zone_param_name: str,
        trend_prefix: str = "vpc",
        sim_box_thickness: dict = None,
    ):
    grid_model = project.grid_models[grid_model_name]
    grid3D = grid_model.get_grid(project.current_realisation)
    nz = grid3D.simbox_indexer.dimensions[2] 
    zone_code_names = grid_model.properties[zone_param_name].code_names
    number_of_layers_per_zone, start_layers_per_zone, end_layers_per_zone = get_zone_layer_numbering(grid3D)

    nzones = len(number_of_layers_per_zone)
    nlogs = len(bw_prob_log_names)
    average_prob_zone_layer = np.zeros((nzones, nlogs, nz), dtype=np.float32)
    average_prob_all_layer = np.zeros((nlogs, nz), dtype=np.float32)
    df_dict = {}

    for well_name in well_list:
        bw_well = xtgeo.blockedwell_from_roxar(project,
                    grid_model_name,
                    bw_name,
                    well_name,
                    lognames='all')
        df_dict[well_name] = bw_well.dataframe

    # Average per zone
    for zone_number, zone_name in zone_code_names.items():
        znr = zone_number - 1  # index
        start = start_layers_per_zone[znr]
        end = end_layers_per_zone[znr]
        nlayers = number_of_layers_per_zone[znr]
        if sim_box_thickness is not None:
            print(f"Zone: {zone_number}  SimBox: {sim_box_thickness[zone_number] }   ")
            dz = sim_box_thickness[zone_number] / nlayers
            print(f"dz: {dz} ")
        for log_number, log_name in enumerate(bw_prob_log_names):
            for k in range(start, end +1):
                values = []
                for well_name, df in df_dict.items():
                    selected = (df["K_INDEX"] == k)
                    val = df.loc[selected, log_name]
                    values.extend(val)

                array = np.array(values)
                average_prob_zone_layer[znr, log_number, k] = np.nanmean(array)
#                print(f"zone: {zone_name} log name: {log_name}  layer: {k}  average: {average_prob_zone_layer[znr, log_number, k]}")

            # Save to file as two column file where vertical position is either layer index
            # or position in depth in simbox coordinates relative to top of zone.
            # When using sim box depth, the first point is z = 0 , the last point is z= simbox_thickness
            # Number of points is nlayer + 1 since both endpoints are included.
            trend_file_name = trend_prefix + "_" + zone_name + "_" + log_name
            print(f"Write file: {trend_file_name}  ")
            with open(trend_file_name,"w") as file:
                if sim_box_thickness is not None:
                    # (nlayer + 1) points including endpoints z= 0 and z= simbox_thickness
                    for k in range(start, end+1):
                        z = (k-start)*dz
                        file.write(f"{z:.2f} {average_prob_zone_layer[znr, log_number,k]:.2f}\n")
                    z = (end-start + 1)*dz
                    file.write(f"{z:.2f} {average_prob_zone_layer[znr, log_number,end]:.2f}\n")
                else:
                    # nlayers, one point per layer
                    for k in range(start, end+1):
                        file.write(f"{k-start} {average_prob_zone_layer[znr, log_number,k]:.2f} 0\n")

    # Average over all zones
    start = start_layers_per_zone[0]
    end = end_layers_per_zone[-1]
    for log_number, log_name in enumerate(bw_prob_log_names):
#        print(f"log_number: {log_number}  start: {start} end:  {end} ")
        for k in range(start, end +1):
            values = []
            for well_name, df in df_dict.items():
                selected = (df["K_INDEX"] == k)
                val = df.loc[selected, log_name]
                values.extend(val)
            array = np.array(values)
            average_prob_all_layer[log_number, k] = np.nanmean(array)

        # Save to file as two column file and use layer as vertical location here.
        trend_file_name = trend_prefix + "_" + log_name
        print(f"Write file: {trend_file_name}  ")
        with open(trend_file_name,"w") as file:
            for k in range(start, end+1):
                file.write(f"{k-start} {average_prob_all_layer[log_number,k]}\n")




def get_facies_and_zone_logs(project,
    well_name_list,
    trajectory,
    logrun,
    facies_log_name,
    zone_log_name,
    debug_level
):
    pp = pprint.PrettyPrinter()
    # Get the facies and codes for the facies log
    first = True
    for well_name in well_name_list:
        well = xtgeo.well_from_roxar(project,
                well_name,
                trajectory=trajectory,
                logrun=logrun,
                lognames=[facies_log_name, zone_log_name],
                inclmd=True)

        if debug_level >= Debug.VERY_VERBOSE:
            print(f"--- Get zone log name and code from well {well.name} ")

        current_facies_code_names_dict = well.get_logrecord(facies_log_name)
        current_zone_code_names_dict = well.get_logrecord(zone_log_name)

        if not current_facies_code_names_dict:
            raise ValueError(f"Facies log {facies_log_name} is not found in well {well_name}")
        if not current_zone_code_names_dict:
            raise ValueError(f"Zone log {zone_log_name} is not found in well {well_name}")
            # Check that the facies and codes defined are the same for all wells

        if first:
            facies_code_names_dict = current_facies_code_names_dict
            zone_code_names_dict = current_zone_code_names_dict
            first = False

        for code, name in current_facies_code_names_dict.items():
            if code not in facies_code_names_dict:
                facies_code_names_dict[code] = name

        for code, name in current_zone_code_names_dict.items():
            if code not in zone_code_names_dict:
                zone_code_names_dict[code] = name

    if debug_level >= Debug.VERY_VERBOSE:
        print(f"--- Facies with code in facies log: {facies_log_name}")
        pp.pprint(facies_code_names_dict)
        print(" ")
        print(f"--- Zones with code in zone log: {zone_log_name}")
        pp.pprint(zone_code_names_dict)
        print(" ")

    return facies_code_names_dict, zone_code_names_dict

def read_model_file(model_file_name):
    # YAML file format
    model_file = Path(model_file_name)
    extension = model_file.suffix.lower().strip('.')
    if extension in ['yaml', 'yml']:
        return _read_model_file_yml(model_file_name)
    else:
        raise ValueError(f"Model file name: {model_file_name}  must be in YAML format with file extension 'yml' or 'yaml' ")

def _read_model_file_yml(model_file_name):
    print(f"Read model file: {model_file_name}  ")
    assert model_file_name
    spec_all = readYml(model_file_name)

    parent_kw = 'EstimateBlockedWellProbLogs'
    spec = spec_all[parent_kw] if parent_kw in spec_all else None
    if spec is None:
        raise ValueError(f"Missing keyword: {parent_kw} ")

    output_prefix = get_text_value(spec, parent_kw, 'OutputPrefix')
    modelling_facies_per_zone_input_dict = get_dict(spec, parent_kw, 'ModellingFaciesPerZone')
    debug_level = get_int_value(spec, parent_kw, 'DebugLevel', has_default=True, default_value=0)
    sim_box_thickness_per_zone_dict = get_dict(spec, parent_kw, 'SimBoxThicknessPerZone')

    print(f"Debug level:{debug_level}")
    kw_orig = 'ProbFromOriginalFaciesLog'
    orig_spec_dict = get_dict(spec, parent_kw, kw_orig)
    well_list_unexpanded = get_list(orig_spec_dict, kw_orig, 'Wells')
    trajectory_name = get_text_value(orig_spec_dict, kw_orig, 'TrajectoryName')
    log_run_name = get_text_value(orig_spec_dict, kw_orig, 'LogRun')
    facies_log_name = get_text_value(orig_spec_dict, kw_orig, 'FaciesLogName')
    zone_log_name = get_text_value(orig_spec_dict, kw_orig, 'ZoneLogName')
    facies_mapping_dict = get_dict(orig_spec_dict, kw_orig, 'MergeFacies', accept_none=True)
    prob_cond_dict = get_dict(orig_spec_dict, kw_orig, 'ProbCondMatrix', accept_none=True)

    kw_bw = 'BlockedWellProbLogs'
    blocked_spec_dict = get_dict(spec, parent_kw, kw_bw)
    grid_model_name = get_text_value(blocked_spec_dict, kw_bw, 'GridModelName')
    zone_param_name = get_text_value(blocked_spec_dict, kw_bw, 'ZoneParamName')
    average_prob_log_prefix = get_text_value(blocked_spec_dict, kw_bw, 'AverageProbLogPrefix')
    bw_zone_log_name  = get_text_value(blocked_spec_dict, kw_bw, 'BlockedWellZoneLogName')
    bw_job_name_string = get_text_value(blocked_spec_dict, kw_bw, 'BlockedWellJobNames')
    bias_weighting_dict = get_dict(blocked_spec_dict, kw_orig, 'BiasWeighting', accept_none=True)
    use_largest_facies_prob = get_bool_value(blocked_spec_dict, 'UseOnlyMaxProb')
    # Split each value into list of names
    modelling_facies_dict = {}
    for zone_number, text_string in modelling_facies_per_zone_input_dict.items():
        modelling_facies_dict[zone_number] = text_string.split(' ')

    # Split each value into list of names
    bw_job_names = bw_job_name_string.split(' ')

    params ={}
    params['debug_level'] = debug_level
    params['prefix'] = output_prefix
    params['modelling_facies_per_zone'] = modelling_facies_dict
    params['well_list'] = well_list_unexpanded
    params['trajectory'] = trajectory_name
    params['logrun'] = log_run_name
    params['facies_log_name'] =  facies_log_name
    params['zone_log_name'] = zone_log_name
    params['facies_mapping'] = facies_mapping_dict
    params['bias_weighting'] = bias_weighting_dict
    params['prob_cond'] = prob_cond_dict
    params['grid_model_name'] = grid_model_name
    params['bw_zone_log_name'] = bw_zone_log_name
    params['bw_job_list'] = bw_job_names
    params['tolerance'] = 0.001
    params['use_largest_facies_prob'] =  use_largest_facies_prob
    params['zone_param_name'] = zone_param_name
    params['average_prob_log_prefix'] = average_prob_log_prefix
    params['sim_box_thickness'] = sim_box_thickness_per_zone_dict
    return params

if __name__ == "__main__":
    grid_model_name = "grid_model"
    zone_param_name = "Zone"
    blocked_wells_name = "BW"
    blocked_wells_prob_log_names =[
        "Prob_F1",
        "Prob_F2",
        "Prob_F3",
        "Prob_F4"
    ] 
    well_list =[
        "W1",
        "W2",
        "W3",
    ]
    trend_prefix = "test_vpc"
    average_prob_logs(project,
        grid_model_name,
        blocked_wells_name,
        blocked_wells_prob_log_names,
        well_list,
        zone_param_name,
        trend_prefix=trend_prefix)
