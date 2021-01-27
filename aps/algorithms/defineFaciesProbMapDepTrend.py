#!/bin/env python
# -*- coding: utf-8 -*-

import numpy as np

from aps.utils.roxar.generalFunctionsUsingRoxAPI import set_continuous_3d_parameter_values
from aps.utils.roxar.grid_model import getDiscrete3DParameterValues
from aps.utils.constants.simple import Debug
from aps.algorithms.defineFacies import BaseDefineFacies


class DefineFaciesProbMapDep(BaseDefineFacies):
    def __init__(self, model_file_name, project, debug_level=Debug.OFF):
        super().__init__(model_file_name, project, 'FaciesProbMapDepTrend', debug_level=debug_level)

        self.__zone_azimuth_values = []

    @property
    def zone_azimuth_values(self):
        if not self.__zone_azimuth_values:
            kw = 'ZoneDepositionAzimuthValues'
            obj = self._root.find(kw)
            if obj is not None:
                text = obj.text
                texts = text.split()
                if len(texts) == 1:  # Same azimuth in all zones
                    az = float(texts[0])
                    if not 0.0 <= az <= 360:
                        raise ValueError('Error: The azimuth value(s) must be between 0 and 360 degrees.')
                    self.__zone_azimuth_values = len(self.selected_zone_numbers) * [az]
                elif len(texts) == len(self.selected_zone_numbers):
                    self.__zone_azimuth_values = [float(x) for x in texts]
                else:
                    raise ValueError(
                        'Error: The number of azimuth values must be 1 or correspond to the number of selected zones.'
                    )
        return self.__zone_azimuth_values

    def calculate_facies_probability_parameter(self, debug_level=Debug.OFF):
        # Get facies map grid model and compute statistics per zone
        real_number = 0
        num_stripes = 100

        # Modelling Grid
        grid_model = self.project.grid_models[self.grid_model_name]
        grid_3d = grid_model.get_grid(real_number)
        indexer = grid_3d.simbox_indexer
        dim_i, dim_j, dim_k = indexer.dimensions
        [zone_values, _] = getDiscrete3DParameterValues(
            grid_model, self.zone_parameter_name, real_number, debug_level=debug_level
        )
        [map_facies, facies_code_names] = getDiscrete3DParameterValues(
            grid_model, self.facies_parameter_name, real_number, debug_level=debug_level
        )

        facies_values = []
        facies_names = []
        for elem in facies_code_names:
            facies_values.append(elem)
            facies_names.append(facies_code_names[elem])
        num_facies = len(facies_values)
        probabilities = np.zeros((len(zone_values), num_facies), np.float32)
        stripe_number = np.zeros(len(zone_values), np.float32)

        # Go through zone by zone and compute deposition average
        for idx in range(len(self.selected_zone_numbers)):
            zone_index = self.selected_zone_numbers[idx]
            if self.debug_level >= Debug.ON:
                print("Zone: ", zone_index)
            if zone_index in indexer.zonation:
                layer_ranges = indexer.zonation[zone_index]
                lr = layer_ranges[0]

                cell_nums = indexer.get_cell_numbers_in_range((0, 0, lr.start), (dim_i, dim_j, lr.stop))  # Only top layer
                cell_corners = grid_3d.get_cell_corners(cell_nums)
                cell_centers = grid_3d.get_cell_centers(cell_nums)

                # Normal vector to azimuth
                az = self.zone_azimuth_values[idx]
                alpha = az + 90
                if alpha > 360:
                    alpha = alpha - 360
                alpha = alpha / 360.0 * 2.0 * np.pi
                az = az / 360.0 * 2.0 * np.pi
                nvec = [np.sin(alpha), np.cos(alpha)]
                dvec = [np.sin(az), np.cos(az)]

                # Stripe data
                stripe_width = min(
                    (np.amax(cell_centers[:, 0]) - np.amin(cell_centers[:, 0])),
                    (np.amax(cell_centers[:, 1]) - np.amin(cell_centers[:, 1]))
                ) / num_stripes

                A0 = [0.0, 0.0]
                if np.sign(dvec[0] * dvec[1]) > 0:
                    A0[0] = np.amin(cell_corners[:, 0:8, 0])
                else:
                    A0[0] = np.amax(cell_corners[:, 0:8, 0])
                A0[1] = np.amin(cell_corners[:, 0:4, 1])
                D = cell_centers[:, 0:2] - A0
                Dn = D[:, 1] * nvec[0] - D[:, 0] * nvec[1]

                stripe_no = np.abs(np.ceil(Dn / (stripe_width * (dvec[1] * nvec[0] - dvec[0] * nvec[1]))))
                stripe_number[cell_nums] = stripe_no

                search_indices = [x for x in range(len(stripe_no))]
                for strip in range(int(np.amin(stripe_no)), int(np.amax(stripe_no)) + 1):
                    cells_in_stripe = []
                    i = 0
                    while i < len(search_indices):
                        index = search_indices[i]
                        if stripe_no[index] == strip:
                            cells_in_stripe.append(cell_nums[index])
                            # Remove used cells, reduce runtime
                            del search_indices[i]
                        else:
                            i += 1

                    no_cells = len(cells_in_stripe)
                    if no_cells > 0:
                        for facies_idx in range(len(facies_values)):
                            facies = facies_values[facies_idx]
                            probabilities[cells_in_stripe, facies_idx] = np.sum(map_facies[cells_in_stripe] == facies) / no_cells

        # Write the calculated probabilities for the selected zones to 3D parameter
        # If the 3D parameter exist in advance, only the specified zones will be altered
        # while grid cell values for other zones are unchanged.
        set_continuous_3d_parameter_values(
            grid_model, "stripeNumber", stripe_number, self.selected_zone_numbers, real_number, debug_level=debug_level
        )
        for facies_idx in range(len(facies_values)):
            facies = facies_values[facies_idx]
            facies_name = facies_names[facies_idx]
            if facies_name:
                parameter_name = self.probability_parameter_name_prefix + '_' + facies_name
                if self.debug_level >= Debug.ON:
                    print(parameter_name, facies)
                success = set_continuous_3d_parameter_values(
                    grid_model, parameter_name, probabilities[:, facies_idx],
                    self.selected_zone_numbers, real_number, debug_level=debug_level
                )
                if not success:
                    raise ValueError('Error: Grid model is empty or can not be updated.')
