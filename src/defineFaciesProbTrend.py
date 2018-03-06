#!/bin/env python
# -*- coding: utf-8 -*-
import roxar

import copy

import numpy as np

import src.generalFunctionsUsingRoxAPI as gf
from src.defineFacies import BaseDefineFacies
from src.utils.constants.simple import Debug
from src.utils.exceptions.xml import MissingKeyword


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
                            print('fname, fnameInReal,prob: ' + facies_name + ' ' + facies_name_in_real + ' ' + str(prob))
                        line = [facies_name, facies_name_in_real, prob]
                        self.__probability_matrix.append(line)
                    else:
                        raise MissingKeyword(kw, self._model_file_name)
            else:
                raise MissingKeyword(kw, self._model_file_name)
        return self.__probability_matrix

    def calculate_facies_probability_parameter(self, debug_level=Debug.OFF):
        # Get grid model and grid model parameter
        eps = 0.00001
        real_number = 0
        grid_model = self.project.grid_models[self.grid_model_name]
        [zone_values, _] = gf.getDiscrete3DParameterValues(
            grid_model, self.zone_parameter_name, real_number, debug_level
        )
        [facies_real_values, code_names_facies] = gf.getDiscrete3DParameterValues(
            grid_model, self.facies_parameter_name, real_number, debug_level
        )

        # Find facies
        facies_names = []
        facies_names_in_real = []
        for item in self.probability_matrix:
            facies_name = item[0]
            facies_name_in_real = item[1]
            if facies_name not in facies_names:
                facies_names.append(copy.copy(facies_name))

            if facies_name_in_real not in facies_names_in_real:
                facies_names_in_real.append(copy.copy(facies_name_in_real))

        if self.debug_level >= Debug.VERBOSE:
            print('Facies names:')
            print(repr(facies_names))

            print('Facies names in input:')
            print(repr(facies_names_in_real))

            print('CodeNamesFacies:')
            print(repr(code_names_facies))

        prob_index = self.calculate_probability_indices(code_names_facies, facies_names_in_real, facies_real_values)

        # probability matrix using indices corresponding to the lists faciesNames and faciesNamesInReal
        probabilities = self.calculate_probabilities(facies_names, facies_names_in_real)
        num_facies = len(facies_names)
        num_facies_in_real = len(facies_names_in_real)

        # Check that probabilities specified are normalized
        for j in range(num_facies_in_real):
            sum_prob = sum([probabilities[i, j] for i in range(num_facies)])
            if abs(sum_prob - 1.0) > eps:
                raise ValueError(
                    'Error: Specified probabilities for facies in regions with name: {} does not sum up to 1.0'
                    ''.format(facies_names_in_real[j])
                 )
        if self.debug_level >= Debug.VERBOSE:
            print('Probability matrix')
            print(repr(probabilities))
        if self.debug_level >= Debug.ON:
            print('Start calculate new probabilities for selected zones for each specified facies')
        sum_probability_values = np.zeros(len(zone_values), np.float32)
        for f in range(num_facies):
            facies_name = facies_names[f]
            if self.debug_level >= Debug.ON:
                print('Facies name: ' + facies_name)

            parameter_name = self.probability_parameter_name_prefix + '_' + facies_name
            if self.debug_level >= Debug.ON:
                print('Parameter: ' + parameter_name)

            parameter_name_cum = self.probability_parameter_name_prefix + '_cum_' + facies_name
            if self.debug_level >= Debug.ON:
                print('Parameter for cum prob: ' + parameter_name_cum)

            # Create new array with 0 probabilities for this facies
            probability_values = np.zeros(len(zone_values), np.float32)
            for zone_number in self.selected_zone_numbers:
                # Filter out cells with selected zone numbers
                [num_defined_cells, cell_index] = gf.getCellValuesFilteredOnDiscreteParam(zone_number + 1, zone_values)
                for i in range(num_defined_cells):
                    index = cell_index[i]
                    code = facies_real_values[index]
                    p_index = prob_index[code]
                    probability_values[index] = probabilities[f, p_index]

            # Calculate cumulative prob of all previously processed facies including current
            sum_probability_values += probability_values

            # Write the calculated probabilities for the selected zones to 3D parameter
            # If the 3D parameter exist in advance, only the specified zones will be altered
            # while grid cell values for other zones are unchanged. 
            success = gf.setContinuous3DParameterValues(
                grid_model, parameter_name, probability_values,
                self.selected_zone_numbers, real_number, debug_level=self.debug_level
            )
            if not success:
                raise ValueError('Error: Grid model is empty or can not be updated.')

            # Write cumulative prob
            success = gf.setContinuous3DParameterValues(
                grid_model, parameter_name_cum, sum_probability_values,
                self.selected_zone_numbers, real_number, debug_level=self.debug_level
            )
            if not success:
                raise ValueError('Error: Grid model is empty or can not be updated.')

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


def run():
    model_file_name = 'defineProbTrend.xml'
    define_facies_trend = DefineFaciesProb(model_file_name, project, debug_level=Debug.OFF)
    define_facies_trend.calculate_facies_probability_parameter()
    print('Finished running defineFaciesProbTrend')


if __name__ == "__main__":
    run()
