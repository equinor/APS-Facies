#!/bin/env python
# -*- coding: utf-8 -*-
import copy
import numpy as np
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List
from aps.utils.roxar.generalFunctionsUsingRoxAPI import set_continuous_3d_parameter_values
from aps.utils.roxar.grid_model import getCellValuesFilteredOnDiscreteParam, getDiscrete3DParameterValues
from aps.algorithms.defineFacies import BaseDefineFacies
from aps.utils.constants.simple import Debug
from aps.utils.exceptions.xml import MissingKeyword
from aps.utils.methods import get_cond_prob_dict
from aps.utils.xmlUtils import getIntCommand
from aps.utils.ymlUtils import get_text_value, get_bool_value, get_dict

class DefineFaciesProb(BaseDefineFacies):
    def __init__(self,
            project=None,
            model_file_name: str = None,
            debug_level: Debug = Debug.OFF,
            grid_model_name: str = None,
            zone_param_name: str =None,
            facies_interpretation_param_name: str = None,
            prefix: str = None,
            selected_zones: List[int] = [],
            use_const_prob: bool = True,
            cond_prob_matrix: List[List] = [],
        ):
        super().__init__(project=project,
            model_file_name=model_file_name,
            trend_keyword='FaciesProbTrend',
            debug_level=debug_level,
            grid_model_name=grid_model_name,
            zone_param_name=zone_param_name,
            facies_interpretation_param_name=facies_interpretation_param_name,
            prefix=prefix,
            selected_zones=selected_zones,
        )
        # Parameters specific for this algorithm
        self._use_const_prob = use_const_prob
        self._probability_matrix = cond_prob_matrix

        if model_file_name is not None:
            if self._file_format == 'yml':
                self._read_model_from_yml(debug_level)
            elif self._file_format == 'xml':
                self._read_model_from_xml_root(debug_level)
            else:
                raise ValueError(f"Model file name: {model_file_name}  must be either 'xml' or 'yml' format")

        # Check that parameters are specified
        if not self._use_const_prob:
            if len(self.probability_matrix) == 0:
                raise ValueError(f"Missing specification of: CondProbMatrix")

    def _read_model_from_xml_root(self, debug_level: Debug = Debug.OFF):
        self._use_const_prob = getIntCommand(self._trend_root, 'UseConstantProbFromVolumeFraction',
                minValue=0, maxValue=1, required=True) == 1
        self._probability_matrix = None
        if not self._use_const_prob:
            cond_prob_matrix = {}
            kw = 'CondProbMatrix'
            obj = self._trend_root.find(kw)
            if obj is None:
                raise KeyError(f"Missing keyword: {kw}")
            for line in obj.findall('Line'):
                text = line.text
                [text1, text2, text3] = text.split()
                facies_name = copy.copy(text1.strip())
                facies_name_in_real = copy.copy(text2.strip())
                prob = float(text3.strip())
                if debug_level >= Debug.VERBOSE:
                    print(f"P({facies_name}|{facies_name_in_real}) = {prob}")
                # When using xml format file, the specification is the same for all selected zones
                for zone_number in self.selected_zone_numbers:
                    key = (zone_number, facies_name, facies_name_in_real)
                    cond_prob_matrix[key] = prob

            self._probability_matrix = cond_prob_matrix

    def _read_model_from_yml(self, debug_level: Debug = Debug.OFF):
        self._use_const_prob = get_bool_value(self._parent_dict,
            'UseConstantProbFromVolumeFraction', True)
        if not self._use_const_prob:
            cond_table = get_dict(self._parent_dict, self._parent_kw, 'CondProbMatrix')
            conditional_prob_facies = get_cond_prob_dict(cond_table, self.selected_zone_numbers)
            self._probability_matrix = conditional_prob_facies
            if debug_level >= Debug.VERBOSE:
                sorted_by_zone_dict = dict(sorted(conditional_prob_facies.items(), key=lambda item: (item[0][0], item [0][2], item[0][1])))
                for key, prob_value in sorted_by_zone_dict.items():
                    (zone_number, facies_name, facies_name_in_real) = key
                    print(f"Zone: {zone_number}  P({facies_name}|{facies_name_in_real}) = {prob_value}")

    @property
    def probability_matrix(self):
        return self._probability_matrix

    @property
    def use_const_prob(self):
        return self._use_const_prob

    def calculate_facies_probability_parameter(self):
        # Get grid model and grid model parameter
        if self.debug_level >= Debug.ON:
            if not self.use_const_prob:
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
            grid_model, self.zone_param_name, real_number
        )
        [facies_real_values, code_names_facies] = getDiscrete3DParameterValues(
            grid_model, self.facies_param_name, real_number
        )

        if not self.use_const_prob:
            # Use conditional probabilities and calculate the probability trend cubes for the modelled facies
            # specified in the conditional probability matrix

            # Find the name of modelled facies from the conditional probability matrix
            facies_names = []
            facies_names_in_real = []
            for key in self.probability_matrix:
                (zone_number, facies_name, facies_name_in_real) = key

                # Create list of modelled facies
                if facies_name not in facies_names:
                    facies_names.append(copy.copy(facies_name))

                # Create list of facies from deterministic facies interpretation
                if facies_name_in_real not in facies_names_in_real:
                    facies_names_in_real.append(copy.copy(facies_name_in_real))

            if self.debug_level >= Debug.VERBOSE:
                print('Facies names to be modelled:')
                for name in facies_names:
                    print(f"   {name}")

                print('Interpreted facies from input facies parameter:')
                for name in facies_names_in_real:
                    print(f"   {name}")

            prob_index = self.calculate_probability_indices(code_names_facies, facies_names_in_real, facies_real_values)

            # probability matrix using indices corresponding to the lists facies_names and facies_names_in_real
            probabilities = self.calculate_probabilities(self.selected_zone_numbers, facies_names, facies_names_in_real)
            num_facies = len(facies_names)
            num_facies_in_real = len(facies_names_in_real)
            num_zones_selected = len(self.selected_zone_numbers)
            eps = 0.00001
            # Check that probabilities specified are normalized
            for k in range(num_zones_selected):
                for j in range(num_facies_in_real):
                    sum_prob = sum(probabilities[k, i, j] for i in range(num_facies))
                    if abs(sum_prob - 1.0) > eps:
                        raise ValueError(
                            f'Error: Probabilities for zone: {self.selected_zone_numbers[k]} for facies in regions '
                            f'with name: {facies_names_in_real[j]} does not sum up to 1.0'
                        )
            if self.debug_level >= Debug.ON:
                print('Calculate facies probability parameters for selected zones')

            for f in range(num_facies):
                facies_name = facies_names[f]
                if self.debug_level >= Debug.ON:
                    print(f"Facies name: {facies_name}")

                # Create a new array with 0 probabilities for this facies
                probability_values = np.zeros(len(zone_values), np.float32)
                for zone_index, zone_number in enumerate(self.selected_zone_numbers):
                    # Filter out cells with selected zone numbers
                    num_defined_cells, cell_index = getCellValuesFilteredOnDiscreteParam(zone_number, zone_values)

                    # Calculate probability values for each cell that belongs to the zone
                    # The code using numpy below is equivalent to the following:
                    #    for i in range(num_defined_cells):
                    #        index = cell_index[i]
                    #        code = facies_real_values[index]
                    #        p_index = prob_index[code]
                    #        probability_values[index] = probabilities[f, p_index]

                    code_array = facies_real_values[cell_index]
                    p_index_array = prob_index[code_array]
                    probability_values[cell_index] = probabilities[zone_index, f, p_index_array]

                parameter_name = self.prefix + '_' + facies_name

                # Write the calculated probabilities for the selected zones to 3D parameter
                # If the 3D parameter exist in advance, only the specified zones will be altered
                # while grid cell values for other zones are unchanged.
                if self.debug_level >= Debug.ON:
                    print(
                        f'Update parameter: {parameter_name} for zones '
                        f'{" ".join(str(zone_number) for zone_number in self.selected_zone_numbers)}:'
                    )
                zone_number_list_zero_indexed = [ znr - 1 for znr in self.selected_zone_numbers]
                success = set_continuous_3d_parameter_values(
                    grid_model, parameter_name, probability_values,
                    zone_number_list_zero_indexed, real_number,
                    is_shared=is_shared, debug_level=self.debug_level
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
            zone_number_list_zero_indexed = [ znr - 1 for znr in self.selected_zone_numbers]
            probability_values = np.zeros(len(zone_values), np.float32)

            for code, facies_name in code_names_facies.items():
                for zone_number in self.selected_zone_numbers:
                    # Filter out cells with the selected zone numbers
                    num_defined_cells, cell_index = getCellValuesFilteredOnDiscreteParam(zone_number, zone_values)
                    selected_cells_facies_for_zone = facies_real_values[
                        (facies_real_values == code) & (zone_values == zone_number)]
                    num_facies_cells = len(selected_cells_facies_for_zone)
                    fraction = num_facies_cells / num_defined_cells

                    if self.debug_level >= Debug.ON:
                        print(
                            f'Average probability (volume fraction) for facies {facies_name} zone {zone_number}  is: {fraction}'
                        )
                    # For all grid cells in zone, assign the fraction
                    probability_values[cell_index] = fraction

                parameter_name = self.prefix + '_' + facies_name

                # Write the calculated probabilities for the selected zones to 3D parameter
                # If the 3D parameter exist in advance, only the specified zones will be altered
                # while grid cell values for other zones are unchanged.
                if self.debug_level >= Debug.ON:
                    print(
                        f'Update parameter: {parameter_name} for '
                        f'zones {" ".join(str(zone_number) for zone_number in self.selected_zone_numbers)}:'
                    )

                success = set_continuous_3d_parameter_values(
                    grid_model, parameter_name, probability_values,
                    zone_number_list_zero_indexed, real_number,
                    is_shared=is_shared, debug_level=self.debug_level
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

    def calculate_probabilities(self, selected_zone_numbers, facies_names, facies_names_in_real):
        num_facies = len(facies_names)
        num_facies_in_real = len(facies_names_in_real)
        num_zones_selected = len(selected_zone_numbers)
        probabilities = np.zeros((num_zones_selected, num_facies, num_facies_in_real), dtype=np.float32)
        for key in self.probability_matrix:
            (zone_number, facies_name, facies_name_in_real) = key
            for zone_index, znr in enumerate(selected_zone_numbers):
                if znr == zone_number:
                    break

            prob = self.probability_matrix[key]
            index1 = facies_names.index(facies_name)
            index2 = facies_names_in_real.index(facies_name_in_real)
            probabilities[zone_index, index1, index2] = prob
        return probabilities
