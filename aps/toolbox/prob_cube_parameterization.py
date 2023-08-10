import roxar
import numpy as np
import math

from pathlib import Path

from aps.utils.constants.simple import Debug, ProbabilityTolerances
from aps.utils.methods import check_missing_keywords_list
from aps.utils.ymlUtils import get_text_value, get_dict, get_bool_value, get_float_value, readYml
from aps.toolbox import check_and_normalise_probability

def run(params):
    """
        Input: Take as input two or more sets of probability cubes and a vector of model parameter.
               The input parameters a[i] are all between 0 and 1 and the sum is 1.
               The input probability cubes must all be conditioned to the probability logs.
        Output: Return updated set of probability cubes by linear combination of input probability cubes.

    Example model file (YAML format):

    ProbCubeUpdate:
    GridModelName: GridModelFine
    ZoneParamName: Zone
    ResultProbParamNamePrefix: Prob_update
    NormalizeInputProb: True
    FaciesPerZone:
      1: F1 F2 F3
      2:      F2      F4
      3:           F3 F4
    WeightsPerZone:
      1:
        SetA: 0.5
        SetB: 0.3
        SetC: 0.2
      2:
        SetA: 0.6
        SetB: 0.2
        SetC: 0.2
      3:
        SetA: 0.4
        SetB: 0.3
        SetC: 0.3

    InputProbParams:
      SetA:
        F1: Prob_A_F1
        F2: Prob_A_F2
        F3: Prob_A_F3
        F4: Prob_A_F4
      SetB:
        F1: Prob_B_F1
        F2: Prob_B_F2
        F3: Prob_B_F3
        F4: Prob_B_F4
      SetC:
        F1: Prob_C_F1
        F2: Prob_C_F2
        F3: Prob_C_F3
        F4: Prob_C_F4


    Example using model file:

    from aps.utils.constants.simple import Debug
    from aps.toolbox.prob_cube_parameterization import run as run_update_prob_cubes
    if __name__ == "__main__":
        params = {
            'project': project,
            'debug_level': Debug.VERBOSE,
            'model_file_name': "examples/prob_cube_update.yml",
        }
        run_update_prob_cubes(params)
    """

    project = params.get('project')
    debug_level = params.get('debug_level', Debug.OFF)
    model_file_name = params.get('model_file_name',None)
    if model_file_name is not None:
        # Read model file
        params = read_model_file(model_file_name, debug_level=debug_level)
        params['project'] = project
        params['debug_level'] = debug_level
    # Check that necessary params are specified
    required_kw_list = [
        "grid_model_name",
        "zone_param_name",
        "prefix",
        "facies",
        "weights",
        "prob_cube_set",
    ]
    check_missing_keywords_list(params, required_kw_list)

    check_normalization(**params)
    calculate_new_probability_cubes(params)
    print("Finished creating new set of probability cubes.")

def read_model_file(model_file_name, debug_level=Debug.OFF):
    # Check suffix of file for file type
    model_file = Path(model_file_name)
    suffix = model_file.suffix.lower().strip('.')
    if suffix in ['yaml', 'yml']:
        param_dict = _read_model_file_yml(model_file_name, debug_level=debug_level)
    else:
        raise ValueError(f"Model file name: {model_file_name}  must be 'yml' format")
    return param_dict

def _read_model_file_yml(model_file_name,
        debug_level=Debug.OFF):

    print(f'Read model file: {model_file_name}')
    spec_all = readYml(model_file_name)

    kw_parent = 'ProbCubeUpdate'
    spec = spec_all[kw_parent] if kw_parent in spec_all else None
    if spec is None:
        raise ValueError(f"Missing keyword: {kw_parent} ")
    grid_model_name = get_text_value(spec, kw_parent, 'GridModelName')
    zone_param_name = get_text_value(spec, kw_parent, 'ZoneParamName')
    result_prefix = get_text_value(spec, kw_parent, 'ResultProbParamNamePrefix')
    should_normalize_input = get_bool_value(spec, 'NormalizeInputProb', default_value=False)
    eps = ProbabilityTolerances.MAX_DEVIATION_BEFORE_ACTION
    kw_facies_per_zone = 'FaciesPerZone'
    facies_names_per_zone_input = get_dict(spec, kw_parent, kw_facies_per_zone)
    if debug_level >= Debug.ON:
        print(f"Should normalize input set of probability cubes:  {should_normalize_input} ")

    # Make a list of all facies in all zones and dict with list of facies names
    facies_names_all_zones = []
    facies_names_per_zone_dict = {}
    for zone_number, facies_names_string in facies_names_per_zone_input.items():
        facies_names = facies_names_string.split()
        facies_names_per_zone_dict[zone_number] = facies_names
        for fname in facies_names:
            if fname not in facies_names_all_zones:
                facies_names_all_zones.append(fname)

    zone_numbers_defined = list(facies_names_per_zone_dict.keys())

    kw_weights = 'WeightsPerZone'
    weights_per_zone_dict = get_dict(spec, kw_parent, kw_weights)

    # Check consistency with facies per zone
    zone_numbers = list(weights_per_zone_dict.keys())
    mismatch_numbers = [n for n in zone_numbers_defined if n not in zone_numbers]
    if len(mismatch_numbers) > 0:
        raise KeyError(
            f" The following zone numbers used in {kw_facies_per_zone} does not exist in  {kw_weights}:\n"
            f" {mismatch_numbers} "
            )
    mismatch_numbers = []
    for n in zone_numbers:
        if n not in zone_numbers_defined:
            mismatch_numbers.append(n)
    if len(mismatch_numbers) > 0:
        raise KeyError(
            f" The following zone numbers used in {kw_weights} is missing in {kw_facies_per_zone}: "
            f" {mismatch_numbers} "
            )
    set_names = None
    for zone_number, weight_dict in weights_per_zone_dict.items():
        if not set_names:
            set_names = list(weight_dict.keys())
        else:
            set_names_current_zone = list(weight_dict.keys())
            for name in set_names_current_zone:
                if name not in set_names:
                    raise KeyError(
                        f"In keyword {kw_weights} there is a mismatch in specification of "
                        "probability cube set for different zones."
                        f"Check if {name} is correct."
                    )

        # Normalize input weights.
        weight_dict = normalize_weights(weight_dict, eps, zone_number, keyword=kw_weights, debug_level=debug_level)
        weights_per_zone_dict[zone_number] = weight_dict

    kw_prob_params_set = 'InputProbParams'
    input_prob_set_dict = get_dict(spec, kw_parent, kw_prob_params_set)

    # Check specification
    for set_name, prob_param_dict in input_prob_set_dict.items():
        if set_name not in set_names:
            raise KeyError(
                f"In keyword {kw_prob_params_set} the specified probability cube set {set_name} "
                f"is not specified in keyword {kw_weights}"
            )
    for set_name in set_names:
        if set_name not in list(input_prob_set_dict.keys()):
            raise KeyError(f"Keyword {kw_prob_params_set} miss specification of probability cube set {set_name}")

    for set_name, prob_param_dict in input_prob_set_dict.items():
        facies_names = list(prob_param_dict.keys())
        # Check that facies names are defined
        mismatch = []
        for fname in facies_names:
            if fname not in facies_names_all_zones:
                mismatch.append(fname)
        if len(mismatch) > 0:
            raise ValueError(f" The following facies names used in keyword {kw_prob_params_set} is not defined in keyword {kw_facies_per_zone}")

    return {
        'grid_model_name': grid_model_name,
        'zone_param_name': zone_param_name,
        'prefix': result_prefix,
        'facies': facies_names_per_zone_dict,
        'weights': weights_per_zone_dict,
        'prob_cube_set': input_prob_set_dict,
        'normalize': should_normalize_input,
        'tolerance': eps,
    }

def check_normalization(
        project,
        grid_model_name,
        zone_param_name,
        facies,
        prob_cube_set,
        normalize,
        tolerance=0.01,
        debug_level=Debug.OFF,
        prefix=None,
        weights=None,
    ):
    facies_names_per_zone_dict = facies
    prob_set_dict = prob_cube_set
    should_normalize = normalize
    tolerance_input = tolerance

    if grid_model_name not in project.grid_models:
        raise ValueError(f"The grid model {grid_model_name} does not exist.")
    grid_model = project.grid_models[grid_model_name]
    if zone_param_name not in grid_model.properties:
        raise ValueError(f"The parameter {zone_param_name} does not exist for grid model {grid_model_name}.")

    facies_names_all = []
    for  facies_names in facies_names_per_zone_dict.values():
        for fname in facies_names:
            if fname not in facies_names_all:
                facies_names_all.append(fname)

    set_names = list(prob_set_dict.keys())
    if should_normalize:
        fraction = 1.0
        tolerance = 1.0
    else:
        fraction = tolerance_input
        tolerance = tolerance_input

    for set_name in set_names:
        prob_param_names_dict = prob_set_dict[set_name]

        input_dict ={
            "project": project,
            "grid_model_name": grid_model_name,
            "modelling_facies_per_zone": facies_names_per_zone_dict,
            "prob_param_per_facies": prob_param_names_dict,
            "overwrite": True,
            "debug_level":  debug_level,
            "tolerance_of_probability_normalisation": tolerance,
            "max_allowed_fraction_of_values_outside_tolerance": fraction,
            "report_zone_regions": False,
        }

        if should_normalize:
            print(f"Normalize probability cube set:  {set_name}")
        else:
            print(f"Check normalization of probability cube set {set_name}")
        check_and_normalise_probability.run(input_dict)




def calculate_new_probability_cubes(param_dict):
    project = param_dict['project']
    debug_level = param_dict['debug_level']
    grid_model_name = param_dict['grid_model_name']
    zone_param_name = param_dict['zone_param_name']
    facies_names_per_zone = param_dict['facies']
    prob_set_dict = param_dict['prob_cube_set']
    weights_per_zone_dict = param_dict['weights']
    prefix = param_dict['prefix']
    eps = param_dict['tolerance']
    should_normalize = param_dict['normalize']

    if debug_level >= Debug.ON:
        print(" ")
        print(f"- Calculate new set of probability cubes")

    grid_model = project.grid_models[grid_model_name]
    zone_param = grid_model.properties[zone_param_name]
    set_names_list = list(prob_set_dict.keys())
    zone_number_list = list(facies_names_per_zone.keys())
    zone_values = zone_param.get_values(project.current_realisation)
    facies_names_all_zones = []
    for zone_number, facies_names in facies_names_per_zone.items():
        for fname in facies_names:
            if fname not in facies_names_all_zones:
                facies_names_all_zones.append(fname)
    number_of_facies_all_zones = len(facies_names_all_zones)

    # Normalize weights
    for zone_number, weight_dict in weights_per_zone_dict.items():
        weight_dict = normalize_weights(weight_dict, eps, zone_number, debug_level=debug_level)
        weights_per_zone_dict[zone_number] = weight_dict

    # Get the prob values from rms input probabilities
    prob_values_dict = {}
    for set_name, prob_param_per_facies_dict in prob_set_dict.items():
        prob_values_dict[set_name] = {}
        for fname, prob_param_name in prob_param_per_facies_dict.items():
            prob_values_dict[set_name][fname] = None
            if prob_param_name not in grid_model.properties:
                raise KeyError(f"The probability parameter: {prob_param_name} does not exist.")
            rms_prob_param = grid_model.properties[prob_param_name]
            if rms_prob_param.is_empty(project.current_realisation):
                raise ValueError(f"The probability parameter: {prob_param_name} is empty. ")
            if debug_level >= Debug.VERBOSE:
                print(f"-- Get prob values for prob cube set: {set_name} for facies: {fname} from {prob_param_name}")
            prob_values_dict[set_name][fname] = rms_prob_param.get_values(project.current_realisation)

    # Calculate updated result probabilities
    sum_values = np.zeros(len(zone_values), dtype=np.float32)
    prob_values_per_facies = np.zeros((number_of_facies_all_zones, len(zone_values)), dtype=np.float32)
    for zone_number in zone_number_list:
        if debug_level >= Debug.VERBOSE:
            print(f"-- Zone number:  {zone_number} ")
        selected_active_cells = (zone_number == zone_values)
        weight_per_set = weights_per_zone_dict[zone_number]
        nactive_in_zone = None

        facies_index = 0
        for facies_name in facies_names_per_zone[zone_number]:
            values_new = prob_values_per_facies[facies_index,:]
            values_new_selected = values_new[selected_active_cells]
            for set_name in set_names_list:
                prob_param_name_dict = prob_set_dict[set_name]
                prob_param_name = prob_param_name_dict[facies_name]
                weight = weight_per_set[set_name]
                values = prob_values_dict[set_name][facies_name]
                nactive_current = len(values[selected_active_cells])

                if nactive_in_zone is None:
                    nactive_in_zone = nactive_current
                else:
                    if nactive_in_zone != nactive_current:
                        raise ValueError(
                            "Expecting the same number of active grid cell values in all probability cubes.\n"
                            f"RMS parameter {prob_param_name} has {nactive_current} active cells in "
                            f"zone {zone_number} while previous probability cube has {nactive_in_zone}."
                        )
                # Calculate linear combination of the probability cubes per zone and per facies
                values_new_selected =  values_new_selected + weight * values[selected_active_cells]

            # Updated values for current facies and current zone
            prob_values_per_facies[facies_index, selected_active_cells] = values_new_selected
            sum_values[selected_active_cells]  = sum_values[selected_active_cells] + values_new_selected
            facies_index += 1

        checked_values = (sum_values[selected_active_cells] > 1-eps) & (sum_values[selected_active_cells] < 1+eps)
        if debug_level >= Debug.VERBOSE:
            print(f"-- Check normalization of new set of probability cubes.")
        if not np.all(checked_values):
            raise ValueError(f"The updated facies probabilities is not normalized within the tolerance {eps} around 1.0")

    # Update RMS project with the new probabilities
    facies_index = 0
    for facies_name in facies_names_all_zones:
        prob_param_name_new = prefix + "_" + facies_name
        values_new = prob_values_per_facies[facies_index,:]
        if prob_param_name_new not in grid_model.properties:
            if debug_level >= Debug.ON:
                print(f"- Create {prob_param_name_new} in grid model {grid_model_name}")

            grid_model.properties.create(prob_param_name_new, property_type=roxar.GridPropertyType.continuous, data_type=np.float32)
            grid_model.properties[prob_param_name_new].set_values(values_new)
        else:
            if debug_level >= Debug.ON:
                print(f"- Updating {prob_param_name_new} in grid model {grid_model_name}")
            grid_model.properties[prob_param_name_new].set_values(values_new)
        facies_index += 1


def normalize_weights(weight_dict, eps, zone_number, keyword=None, debug_level=Debug.OFF):
    # Normalize weights
    sum_weights = 0
    truncate = False
    for key, weight_value in weight_dict.items():
        if weight_value < 0.0:
            truncate = True
            weight_value = 0.0
        elif weight_value > 1.0:
            truncate = True
            weight_value = 1.0
        sum_weights += float(weight_value)

    if debug_level >= Debug.ON:
        print(f"- Input weights for zone {zone_number} : {list(weight_dict.values())} ")
        if truncate:
            print(f"- Warning: Some input weights are outside interval[0,1] and are truncated for {zone_number}.")
    if sum_weights == 0:
        if keyword:
            err_msg = f"The weights in keyword {keyword} for zone {zone_number} are all zero "
        else:
            err_msg = f"The weights for some probability cube set are all zero "
        raise ValueError(err_msg)

    if math.fabs(sum_weights - 1.0) > eps:
        for key, weight_value in weight_dict.items():
            normalized_weight_value = weight_value/sum_weights
            weight_dict[key] =  normalized_weight_value

    if debug_level >= Debug.ON:
        print(f"- Normalized weights for zone {zone_number} : {list(weight_dict.values())} ")

    return weight_dict