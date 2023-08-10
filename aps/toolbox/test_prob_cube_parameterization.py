from aps.utils.constants.simple import Debug
from aps.toolbox.prob_cube_parameterization import run as run_update_prob_cubes

if __name__ == "__main__":

    facies_names_per_zone_dict =  {
        1: ["F1", "F2", "F3", "F4", "F5"],
        2: ["F1", "F2", "F3", "F4", "F5"],
        3: ["F1", "F2", "F3", "F4", "F5"],
        4: ["F1", "F2", "F3", "F4", "F5"],
        5: ["F1", "F2", "F3", "F4", "F5"],
        6: ["F1", "F2", "F3", "F4", "F5"],
    }

    weights_per_zone_dict = {
        1: {
            "SetA": 0.5,
            "SetB": 0.3,
            "SetC": 0.2,
        },
        2: {
            "SetA": 0.6,
            "SetB": 0.2,
            "SetC": 0.2,
        },
        3: {
            "SetA": 0.4,
            "SetB": 0.3,
            "SetC": 0.3,
        },
        4: {
            "SetA": 0.9,
            "SetB": 0.05,
            "SetC": 0.05,
        },
        5: {
            "SetA": 1.0,
            "SetB": 0.0,
            "SetC": 0.0,
        },
        6: {
            "SetA": 1.0,
            "SetB": 0.0,
            "SetC": 0.0,
        },
    }

    input_prob_set_dict = {
        "SetA": {
            "F1": "Prob_A_F1",
            "F2": "Prob_A_F2",
            "F3": "Prob_A_F3",
            "F4": "Prob_A_F4",
            "F5": "Prob_A_F5",
        },
        "SetB": {
            "F1": "Prob_B_F1",
            "F2": "Prob_B_F2",
            "F3": "Prob_B_F3",
            "F4": "Prob_B_F4",
            "F5": "Prob_B_F5",
        },
        "SetC": {
            "F1": "Prob_C_F1",
            "F2": "Prob_C_F2",
            "F3": "Prob_C_F3",
            "F4": "Prob_C_F4",
            "F5": "Prob_C_F5",
        },
    }

    params = {
        'project': project,
        'debug_level': Debug.VERBOSE,
        'grid_model_name': 'GridModelFine',
        'zone_param_name': 'Zone',
        'prefix': "Prob_update",
        'facies': facies_names_per_zone_dict,
        'weights': weights_per_zone_dict,
        'prob_cube_set': input_prob_set_dict,
        'normalize': False,
        'tolerance': 0.01,
    }
    # Alternative specification using model file in yml format:
    # params = {
    #     'project': project,
    #     'debug_level': Debug.VERBOSE,
    #     'model_file_name': "examples/prob_cube_update.yml",
    # }

    run_update_prob_cubes(params)