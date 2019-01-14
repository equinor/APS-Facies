# -*- coding: utf-8 -*-
import numpy as np
from src.utils.constants.simple import VariogramType, Debug


def isVariogramTypeOK(_type, debug_level=Debug.OFF):
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
        print('''Error: Specified variogram : {variogram_type} is not implemented
Error: Allowed variograms are:
       SPHERICAL
       EXPONENTIAL
       GAUSSIAN
       GENERAL_EXPONENTIAL
       MATERN32
       MATERN52
       MATERN72
       CONSTANT
'''.format(variogram_type=_type.name))
    return False


def check_probability_values(prob_values, tolerance_of_probability_normalisation,
                             facies_name=" ", parameter_name=" ",
                             max_allowed_fraction_of_values_outside_tolerance=0.1):
    ''' The input numpy array prob_values is checked that the values are legal probabilities. A tolerance is accepted.
        Returns prob_values in [0,1] and raise error if illegal probability values (outside tolerance)
    '''
    num_defined_cells = len(prob_values)
    if num_defined_cells == 0:
        return prob_values

    num_negative = 0
    num_above_one = 0

    # numpy vector with 0 and 1 values with value 1 if the test is true and 0 if false
    check_value = (prob_values < -tolerance_of_probability_normalisation)
    # The sum will be equal to the number of cells with value 1 in check_value
    num_negative = check_value.sum()

    check_value = (prob_values > 1.0 + tolerance_of_probability_normalisation)
    num_above_one = check_value.sum()

    num_defined_cells = len(prob_values)

    negative_fraction = num_negative / num_defined_cells
    if negative_fraction >  max_allowed_fraction_of_values_outside_tolerance:
        raise ValueError(
            'Probability for facies {} in {} has {} negative values.'
            ''.format(facies_name, parameter_name, num_negative)
            )

    above_one_fraction = num_above_one / num_defined_cells
    if above_one_fraction >  max_allowed_fraction_of_values_outside_tolerance:
        raise ValueError(
            'Probability for facies {} in {} has {} values above 1.0'
            ''.format(facies_name, parameter_name, num_above_one)
            )

    prob_values[prob_values < 0.0] = 0.0
    prob_values[prob_values > 1.0] = 1.0
    return prob_values


def check_probability_normalisation(sum_probability_values, eps, tolerance_of_probability_normalisation,
                                    max_allowed_fraction_of_values_outside_tolerance=0.1):
    num_defined_cells = len(sum_probability_values)
    ones = np.ones(num_defined_cells, np.float32)
    normalise_is_necessary = False
    if not np.allclose(sum_probability_values, ones, eps):
        normalise_is_necessary = True
        unacceptable_prob_normalisation = 0
        min_acceptable_prob_sum = 1.0 - tolerance_of_probability_normalisation
        max_acceptable_prob_sum = 1.0 + tolerance_of_probability_normalisation

        check_sum_prob = (sum_probability_values < min_acceptable_prob_sum) | (sum_probability_values > max_acceptable_prob_sum)
        unacceptable_prob_normalisation = check_sum_prob.sum()
        unacceptable_prob_normalisation_fraction = unacceptable_prob_normalisation / num_defined_cells

        if unacceptable_prob_normalisation_fraction >  max_allowed_fraction_of_values_outside_tolerance:
            largest_prob_sum = sum_probability_values.max()
            smallest_prob_sum =  sum_probability_values.min()
            raise ValueError(
                'Sum of input facies probabilities is either less than: {} or larger than: {} in: {} cells.\n'
                'Input probabilities should be normalised and the sum close to 1.0 but found a minimum value of: {} and a maximum value of: {}\n'
                'Check input probabilities!'
                ''.format(
                    min_acceptable_prob_sum, max_acceptable_prob_sum,
                    unacceptable_prob_normalisation, smallest_prob_sum, largest_prob_sum
                )
            )
    return normalise_is_necessary
