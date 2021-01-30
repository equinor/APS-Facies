#!/bin/env python
# -*- coding: utf-8 -*-
import copy
import numpy as np

from aps.utils.roxar.generalFunctionsUsingRoxAPI import set_continuous_3d_parameter_values
from aps.utils.roxar.grid_model import getCellValuesFilteredOnDiscreteParam, getDiscrete3DParameterValues
from aps.algorithms.defineFacies import BaseDefineFacies
from aps.utils.constants.simple import Debug
from aps.utils.exceptions.xml import MissingKeyword


class DefineFaciesProb(BaseDefineFacies):
    def __init__(self, model_file_name, project, debug_level=Debug.OFF):
        super().__init__(model_file_name, project, 'FaciesProbTrend', debug_level)

        self.__probability_matrix = []

    @property
    def probability_matrix(self):
        if not self.__probability_matrix:
            kw = 'CondProbMatrix'
            obj = self._root.find(kw)
            if obj is not None:
                kw = 'Line'
                for line in obj.findall(kw):
                    if line is not None:
                        text = line.text
                        [text1, text2, text3] = text.split()
                        facies_name = copy.copy(text1.strip())
                        facies_name_in_real = copy.copy(text2.strip())
                        prob = float(text3.strip())
                        if self.debug_level >= Debug.VERBOSE:
                            print(f'fname, fnameInReal ,prob: {facies_name} {facies_name_in_real} {prob}')
                        line = [facies_name, facies_name_in_real, prob]
                        self.__probability_matrix.append(line)
                    else:
                        raise MissingKeyword(kw, self._model_file_name)
            else:
                raise MissingKeyword(kw, self._model_file_name)
        return self.__probability_matrix

    def calculate_facies_probability_parameter(self, debug_level=Debug.VERBOSE):
        # Get grid model and grid model parameter
        self.debug_level = Debug.ON
        use_const_prob_trend = int(self.use_const_prob_from_vol_fraction)
        if self.debug_level >= Debug.ON:
            if not use_const_prob_trend:
                print(
                    'Calculate probability cubes having trends in each zone '
                    'defined by the RMS discrete 3D parameter input'
                )
            else:
                print(
                    'Calculate probability cubes which have constant values in '
                    'each zone as average probability (volume fraction)'
                )
        real_number = self.project.current_realisation
        grid_model = self.project.grid_models[self.grid_model_name]
        is_shared = grid_model.shared
        [zone_values, _] = getDiscrete3DParameterValues(
            grid_model, self.zone_parameter_name, real_number, debug_level
        )
        [facies_real_values, code_names_facies] = getDiscrete3DParameterValues(
            grid_model, self.facies_parameter_name, real_number, debug_level
        )

        if use_const_prob_trend == 0:
            # Use conditional probabilities and calculate the probability trend cubes for the modelled facies
            # specified in the conditional probability matrix

            # Find the name of modelled facies from the conditional probability matrix
            facies_names = []
            facies_names_in_real = []
            for item in self.probability_matrix:
                # Create list of modelled facies
                facies_name = item[0]
                facies_name_in_real = item[1]
                if facies_name not in facies_names:
                    facies_names.append(copy.copy(facies_name))

                # Create list of facies from deterministic facies interpretation
                if facies_name_in_real not in facies_names_in_real:
                    facies_names_in_real.append(copy.copy(facies_name_in_real))

            if self.debug_level >= Debug.VERBOSE:
                print('Facies names to be modelled:')
                for name in facies_names:
                    print('   {}'.format(name))

                print('Interpreted facies from input facies parameter:')
                for name in facies_names_in_real:
                    print(f'   {name}')

                print('Facies codes in input facies parameter:')
                print(repr(code_names_facies))

            prob_index = self.calculate_probability_indices(code_names_facies, facies_names_in_real, facies_real_values)

            # probability matrix using indices corresponding to the lists facies_names and facies_names_in_real
            probabilities = self.calculate_probabilities(facies_names, facies_names_in_real)
            num_facies = len(facies_names)
            num_facies_in_real = len(facies_names_in_real)

            eps = 0.00001
            # Check that probabilities specified are normalized
            for j in range(num_facies_in_real):
                sum_prob = sum(probabilities[i, j] for i in range(num_facies))
                if abs(sum_prob - 1.0) > eps:
                    raise ValueError(
                        f'Error: Specified probabilities for facies in regions '
                        f'with name: {facies_names_in_real[j]} does not sum up to 1.0'
                    )
            if self.debug_level >= Debug.VERBOSE:
                print('Probability matrix')
                print(repr(probabilities))
            if self.debug_level >= Debug.ON:
                print('Start calculate new probabilities for selected zones for each specified facies to be modelled')

            for f in range(num_facies):
                facies_name = facies_names[f]
                if self.debug_level >= Debug.ON:
                    print('Facies name: ' + facies_name)

                # Create a new array with 0 probabilities for this facies
                probability_values = np.zeros(len(zone_values), np.float32)
                for zone_number in self.selected_zone_numbers:
                    # Filter out cells with selected zone numbers
                    num_defined_cells, cell_index = getCellValuesFilteredOnDiscreteParam(zone_number + 1, zone_values)

                    # Calculate probability values for each cell that belongs to the zone
                    # The code using numpy below is equivalent to the following:
                    #    for i in range(num_defined_cells):
                    #        index = cell_index[i]
                    #        code = facies_real_values[index]
                    #        p_index = prob_index[code]
                    #        probability_values[index] = probabilities[f, p_index]

                    code_array = facies_real_values[cell_index]
                    p_index_array = prob_index[code_array]
                    probability_values[cell_index] = probabilities[f, p_index_array]

                parameter_name = self.probability_parameter_name_prefix + '_' + facies_name

                # Write the calculated probabilities for the selected zones to 3D parameter
                # If the 3D parameter exist in advance, only the specified zones will be altered
                # while grid cell values for other zones are unchanged.
                if self.debug_level >= Debug.ON:
                    print(
                        f'Update parameter: {parameter_name} for zones '
                        f'{" ".join(str(zone_number + 1) for zone_number in self.selected_zone_numbers)}:'
                    )

                success = set_continuous_3d_parameter_values(
                    grid_model, parameter_name, probability_values,
                    self.selected_zone_numbers, real_number, is_shared=is_shared, debug_level=self.debug_level
                )
                if not success:
                    raise ValueError('Error: Grid model is empty or can not be updated.')
                # End loop over facies
        else:
            # Calculate average volume fraction of each facies in the zone and set the probability
            # cubes for these facies equal to the average volume fraction
            # Note that in this case no name of modelled facies is written and the facies names used in
            # input (intepreted) facies realization is used as facies names for the probability cubes.

            # Create a new array with 0 probabilities for this facies
            probability_values = np.zeros(len(zone_values), np.float32)

            for code, facies_name in code_names_facies.items():
                for zone_number in self.selected_zone_numbers:
                    zone_num = zone_number + 1
                    # Filter out cells with the selected zone numbers
                    num_defined_cells, cell_index = getCellValuesFilteredOnDiscreteParam(zone_num, zone_values)
                    selected_cells_facies_for_zone = facies_real_values[
                        (facies_real_values == code) & (zone_values == zone_num)]
                    num_facies_cells = len(selected_cells_facies_for_zone)
                    fraction = num_facies_cells / num_defined_cells

                    if self.debug_level >= Debug.ON:
                        print(
                            f'Average probability (volume fraction) for facies {facies_name} zone {zone_num}  is: {fraction}'
                        )
                    # For all grid cells in zone, assign the fraction
                    probability_values[cell_index] = fraction

                parameter_name = self.probability_parameter_name_prefix + '_' + facies_name

                # Write the calculated probabilities for the selected zones to 3D parameter
                # If the 3D parameter exist in advance, only the specified zones will be altered
                # while grid cell values for other zones are unchanged.
                if self.debug_level >= Debug.ON:
                    print(
                        f'Update parameter: {parameter_name} for '
                        f'zones {" ".join(str(zone_number + 1) for zone_number in self.selected_zone_numbers)}:'
                    )

                success = set_continuous_3d_parameter_values(
                    grid_model, parameter_name, probability_values,
                    self.selected_zone_numbers, real_number, is_shared=is_shared, debug_level=self.debug_level
                )
                if not success:
                    raise ValueError('Error: Grid model is empty or can not be updated.')

    # End of calculate_facies_probability_parameter

    @staticmethod
    def calculate_probability_indices(code_names_facies, facies_names_in_real, facies_real_values):
        minimum = np.min(facies_real_values)
        maximum = np.max(facies_real_values)

        prob_index = np.zeros(maximum + 1, np.int)
        for i in range(maximum):
            prob_index[i] = -1
        for i in range(len(facies_names_in_real)):
            facies_name = facies_names_in_real[i]
            for code in range(minimum, maximum + 1):
                if code in code_names_facies and facies_name == code_names_facies[code]:
                    prob_index[code] = i
        return prob_index

    def calculate_probabilities(self, facies_names, facies_names_in_real):
        num_facies = len(facies_names)
        num_facies_in_real = len(facies_names_in_real)

        probabilities = np.zeros((num_facies, num_facies_in_real), dtype=np.float32)
        for item in self.probability_matrix:
            facies_name = item[0]
            facies_name_in_real = item[1]
            prob = item[2]

            index1 = facies_names.index(facies_name)
            index2 = facies_names_in_real.index(facies_name_in_real)

            probabilities[index1, index2] = prob
        return probabilities
