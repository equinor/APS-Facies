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
from aps.utils.methods import get_debug_level, get_specification_file


def run(roxar=None, project=None, **kwargs):
    model_file_name = get_specification_file(**kwargs)
    debug_level = get_debug_level(**kwargs)
    define_facies_trend = DefineFaciesProbMapDep(model_file_name, project)
    define_facies_trend.calculate_facies_probability_parameter()
    print('Finished running defineFaciesProbMapDepTrend')


if __name__ == '__main__':
    import roxar
    run(roxar, project)
