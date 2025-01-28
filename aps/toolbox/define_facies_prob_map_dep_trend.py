#!/bin/env python
# -*- coding: utf-8 -*-
"""
Description:
    The script calculates a one dimensional trend of volume fraction of each category (facies) in an input RMS discrete 3D parameter.
    The output is a 3D RMS parameter of type continuous containing the volume fraction of each category (facies) input RMS discrete 3D parameter.
    The user specify a direction, an azimuth angle and in this direction a set of stripes orthogonal to the specified direction is defined.
    The width of each such stripe is hard coded but relatively small. Each such stripe define an area in which the volume fraction of each
    category or facies is calculated. This creates a 1 dimensional trend varying in the azimuth direction but not orthogonal to the azimuth direction.
    This type of trend can be used to as facies probabilities  in cases one want to use trends in probability instead of in Gaussian fields in
    the APS method. The trend created here is a bit experimental and is probably only relevant if the depositional system of facies has a clear
    direction that can be identified and specified as the azimuth angle.

    The input is specified in a model file (xml format file).

Example of model file:
    <?xml version="1.0" ?>
    <APS_prob_trend>
        <FaciesProbMapDepTrend>
            <GridModelName>   GridModel1 </GridModelName>
             <ZoneParamName>  Zone </ZoneParamName>
             <FaciesParamName>  DiscreteParam </FaciesParamName>
             <ProbParamNamePrefix>  ProbTrend  </ProbParamNamePrefix>
             <SelectedZones> 1  </SelectedZones>
             <ZoneDepositionAzimuthValues> 35   </ZoneDepositionAzimuthValues>
             <!-- Either one azimuth value used for all zones or one value per zone -->
        </FaciesProbMapDepTrend>
    </APS_prob_trend>

    Comments to the model file specification:
    The keyword SelectedZone can have number of one or more zones. If more than one zone number is specified,
    the same setting is defined to be used for all these zones when calculating the facies (categorical variable) probability trend.
    The keyword ZoneDepositionalAzimuthValues specify one angle per zone in degrees. If only one angle is specified but more than one
    zone number is specified in keyword SelectedZones, then the same angle is used for all these zones.
"""
from aps.algorithms.defineFaciesProbMapDepTrend import DefineFaciesProbMapDep


def run(kwargs):
    """
        Create probability trend where probability is estimated from input facies parameter
        for stripes ortogonal to the specified depositional direction.

        Usage alternatives:
        - Specify input dictionary with name of model file where all input information is specified. See example 1.
        - Specify input dictionary with all input information. See example 2.

Example 1:

from aps.toolbox import define_facies_prob_map_dep_trend
from aps.utils.constants.simple import Debug

kwargs = {
    "project": project,
    "debug_level": Debug.VERBOSE,
    "model_file_name": "examples/test_define_prob_map_dep_trend2.xml",
}
define_facies_prob_map_dep_trend(kwargs)


Example 2:

from aps.toolbox import define_facies_prob_map_dep_trend
from aps.utils.constants.simple import Debug

selected_zones = [1,2,3]
zone_azimuth_values =[45.0,35.0,25.0]
kwargs = {
    "project": project,
    "debug_level": Debug.VERBOSE,
    "grid_model_name": "GridModelFine",
    "zone_param_name": "Zone",
    "facies_interpretation_param_name": "Deterministic_facies",
    "prefix": "ProbTestDep1",
    "selected_zones": selected_zones,
    "zone_azimuth_values": zone_azimuth_values,
    "resolution": 25,
}
define_facies_prob_map_dep_trend(kwargs)

    """
    define_facies_trend = DefineFaciesProbMapDep(**kwargs)
    define_facies_trend.calculate_facies_probability_parameter()
    print('Finished running define_facies_prob_map_dep_trend')
