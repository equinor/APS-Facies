# -*- coding: utf-8 -*-
import difflib
from filecmp import cmp
from os.path import exists
from typing import Union

import numpy as np
from aps.utils.constants.simple import VariogramType, Debug


class NormalisationError(ValueError):
    pass


def isVariogramTypeOK(
    _type: Union[VariogramType, str], debug_level: Debug = Debug.OFF
) -> bool:
    if isinstance(_type, str):
        try:
            VariogramType[_type]
        except KeyError:
            return False
        return True
    elif _type in VariogramType:
        return True
    elif _type._name_ in VariogramType._member_map_:
        # Hack because of some strange bug (apparently variogramType is not an instance in VariogramType (class-wise))
        # even though they are
        return True
    elif debug_level >= Debug.VERY_VERBOSE:
        print(f"""Error: Specified variogram : {_type.name} is not implemented
Error: Allowed variograms are:
       SPHERICAL
       EXPONENTIAL
       GAUSSIAN
       GENERAL_EXPONENTIAL
       MATERN32
       MATERN52
       MATERN72
       CONSTANT
""")
    return False


def check_probability_values(
    prob_values: np.ndarray,
    tolerance_of_probability_normalisation: float,
    max_allowed_fraction_with_mismatch: float,
    facies_name: str = ' ',
    parameter_name: str = ' ',
    stop_on_error: bool = True,
    error_dict: dict = None,
):
    """The input numpy array prob_values is checked that the values are legal probabilities. A tolerance is accepted.
    Returns prob_values in [0,1] and raise error if illegal probability values (outside tolerance)
    """
    err_found = False
    num_defined_cells = len(prob_values)
    if num_defined_cells == 0:
        return prob_values, error_dict

    # numpy vector with 0 and 1 values with value 1 if the test is true and 0 if false
    check_value = prob_values < -tolerance_of_probability_normalisation
    # The sum will be equal to the number of cells with value 1 in check_value
    num_negative = check_value.sum()

    check_value = prob_values > 1.0 + tolerance_of_probability_normalisation
    num_above_one = check_value.sum()

    negative_fraction = num_negative / num_defined_cells
    if negative_fraction > max_allowed_fraction_with_mismatch:
        err_list = []
        err_list.append(f'Facies: {facies_name}  Parameter name: {parameter_name}')
        err_list.append(
            f'Number of grid cells with probability values < {-tolerance_of_probability_normalisation}:  {num_negative}'
        )
        err_list.append(
            f'Fraction of grid cells with probability values  < {-tolerance_of_probability_normalisation}:  {negative_fraction * 100:.2f}%'
        )
        if stop_on_error:
            for item in err_list:
                print(item)
            raise ValueError('Normalisation error found')
        error_dict['Message'] += err_list
        error_dict['Error'] = True
        err_found = True

    above_one_fraction = num_above_one / num_defined_cells
    if above_one_fraction > max_allowed_fraction_with_mismatch:
        err_list = []
        err_list.append(f'Facies: {facies_name}  Parameter name: {parameter_name}')
        err_list.append(
            f'Number of grid cells with probability values > {1.0 + tolerance_of_probability_normalisation}:  {num_above_one}'
        )
        err_list.append(
            f'Fraction of grid cells probability values  > {1.0 + tolerance_of_probability_normalisation}:  {above_one_fraction * 100:.2f}%'
        )
        if stop_on_error:
            for item in err_list:
                print(item)
            raise ValueError('Normalisation error found')
        error_dict['Message'] += err_list
        error_dict['Error'] = True
        err_found = True

    prob_values[prob_values < 0.0] = 0.0
    prob_values[prob_values > 1.0] = 1.0
    if stop_on_error:
        return prob_values
    else:
        return prob_values, error_dict, err_found


def check_probability_normalisation(
    sum_probability_values: np.ndarray,
    eps: float,
    tolerance_of_probability_normalisation: float,
    max_allowed_fraction_with_mismatch: float,
    stop_on_error: bool = True,
    error_dict: dict = None,
):
    err_found = False
    num_defined_cells = len(sum_probability_values)
    ones = np.ones(num_defined_cells, np.float32)
    low_tolerance = 1.0 - tolerance_of_probability_normalisation
    high_tolerance = 1.0 + tolerance_of_probability_normalisation
    normalise_is_necessary = False
    if not np.allclose(sum_probability_values, ones, eps):
        normalise_is_necessary = True
        min_acceptable_prob_sum = low_tolerance
        max_acceptable_prob_sum = high_tolerance

        check_sum_prob = (sum_probability_values < min_acceptable_prob_sum) | (
            sum_probability_values > max_acceptable_prob_sum
        )
        unacceptable_prob_normalisation = check_sum_prob.sum()
        unacceptable_prob_normalisation_fraction = (
            unacceptable_prob_normalisation / num_defined_cells
        )

        if (
            unacceptable_prob_normalisation_fraction
            > max_allowed_fraction_with_mismatch
        ):
            largest_prob_sum = sum_probability_values.max()
            smallest_prob_sum = sum_probability_values.min()
            err_list = []
            err_list.append('Check normalization of facies probabilities.')
            err_list.append(
                f'Tolerance interval is: [{low_tolerance}, {high_tolerance}]'
            )
            err_list.append(
                f'Number of grid cells with probabilities summing up to value outside tolerance interval: {unacceptable_prob_normalisation}'
            )
            err_list.append(
                f'Fraction of grid cells outside tolerance: {unacceptable_prob_normalisation_fraction * 100:.2f}%'
            )
            err_list.append(
                f'Max limit of mismatch fraction specified: {max_allowed_fraction_with_mismatch * 100:.2f}%'
            )
            err_list.append(f'Minimum sum of probabilities found: {smallest_prob_sum}')
            err_list.append(f'Maximum sum of probability found: {largest_prob_sum}')
            err_list.append(
                'If you think the probability cubes are OK anyway, you may increase the maximum fraction in project settings to '
            )
            err_list.append(
                f'at least {unacceptable_prob_normalisation_fraction * 100:.2f}%.'
            )
            if stop_on_error:
                for item in err_list:
                    print(item)
                raise NormalisationError('Normalisation errors found')
            error_dict['Message'] += err_list
            error_dict['Error'] = True
            err_found = True

    if stop_on_error:
        return normalise_is_necessary
    else:
        return normalise_is_necessary, error_dict, err_found


def compare(
    source: str,
    reference: str,
    verbose: bool = True,
) -> bool:
    prefix = ''
    if not exists(reference):
        prefix = 'aps/unit_test/'
        if not exists(prefix + reference):
            prefix += 'integration/'
    check = cmp(prefix + reference, source)

    if verbose:
        if check:
            print('Files are equal. OK')
        else:
            with (
                open(source, encoding='utf-8') as f,
                open(reference, encoding='utf-8') as ref,
            ):
                diff = difflib.Differ().compare(
                    f.readlines(),
                    ref.readlines(),
                )
            print('Files are different. NOT OK')
            print(''.join(diff))
    return check
