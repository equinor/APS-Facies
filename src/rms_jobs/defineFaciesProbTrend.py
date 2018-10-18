#!/bin/env python
# -*- coding: utf-8 -*-
"""Description:
 The script defineFaciesProbTrend can be used to make RMS 3D parameters for facies probabilities to be
 used in APS facies modelling. The output is facies probabilities or in special case volume fraction of each category
 defined in input RMS 3D discrete parameter. A model file (xml file) is specified by the user and define how the
 output probability cubes (RMS3D continuous parameters) is calculated.

 The script take as input an existing RMS 3D discrete parameter (which may be a facies realisation).
 The script will also take as input a probability for the facies to be modelled for each discrete value defined in
 the input RMS 3D parameter.
 For example, if the input contains 3 different values corresponding to the three values for the code names:
    Name  Code
     A     1
     B     2
     C     3
 and the user want to model the following facies:
    Name   Code
     F1    1
     F2    2
     F3    3
     F4    4
 then the user must specify conditioned probabilities for each facies to be modelled given
 the category value from input like e.g.
    Prob(F1|A)  = 0.9
    Prob(F2|A)  = 0.05
    Prob(F3|A)  = 0.05
    Prob(F4|A)  = 0.0

    Prob(F1|B)  = 0.10
    Prob(F2|B)  = 0.85
    Prob(F3|B)  = 0.0
    Prob(F4|B)  = 0.05

    Prob(F1|C)  = 0.0
    Prob(F2|C)  = 0.3
    Prob(F3|C)  = 0.7
    Prob(F4|C)  = 0.0
 This means that the output facies probability RMS 3D parameter for F1 is equal to 0.9 for grid cells where
 input RMS 3D parameter has category A, 0.1 in grid cells where input is B, 0.0 in grid cells where
 input is C.
 For facies F2, F3, F4 the procedure for assigning probabilities is the same.
 Note for consistency, the sum of probabilities for F1, F2 F3 and F4 must sum to 1.0 in each grid cell.
 This means that e.g. Prob(F1|A) + Prob(F2|A) + Prob(F3|A) + Prob(F4|A) = 1
 and similar for  grid cell in input where the category is B,C.

 Some special cases of specification:
 - One to one correspondence between facies to be modelled and the input categorical variables:
   Assume the facies numbers of modelled facies is 3, the same as the number of categories of input discrete RMS parameter.
   If Prob(F1|A) = 1.0, Prob(F2|B) = 1.0, Prob(F3|C)= 1.0 (and the rest of the conditioned probabilities are 0), the output
   probabilities will ensure with 100% certainty that the facies realisation from the APS method will be deterministic
   and identical to the input RMS 3D parameter.

 An option is given to the user to specify that the user wants to get as output the average probabilities for each zone instead.
 This means that all grid cells in a zone is assigned the value of the average over all grid cells for the zone.
 The calculation is as follows:
   - First the facies probability cubes are calculated for each output facies.
   - Then the average of the probability within a zone is calculated for each facies.
   - The average is assigned to each grid cell within the zone.
   - The above calculations are done for each zone and each facies.

 A special case of usage of the average probability option is just to set Prob(F1|A) = 1 Prob(F2|B) = 1 Prob(F3|C) = 1.
 In this case the average probabilities calculated is the same as the fraction of grid cells of category A relative
 to all cells in the zone, and so on for B and C also. This is just the volume fraction of A, B and C in each zone and
 the output of facies probability F1 is actually the volume fraction of A.
 probability of F2 is the volume fraction of B and so on.

Example of a model file:
 <?xml version="1.0" ?>
 <APS_prob_trend>
     <FaciesProbTrend>
         <GridModelName>   GridModel1 </GridModelName>
         <ZoneParamName>  Zone </ZoneParamName>
         <FaciesParamName>  DiscreteParam </FaciesParamName>
         <ProbParamNamePrefix>  ProbTrend  </ProbParamNamePrefix>
         <SelectedZones> 1 </SelectedZones>
         <UseConstantProbFromVolumeFraction> 0 </UseConstantProbFromVolumeFraction>
         <CondProbMatrix>
             <Line>  F1  A  0.90 </Line>
             <Line>  F2  A  0.05 </Line>
             <Line>  F3  A  0.0 </Line>
             <Line>  F4  A  0.0 </Line>
             <Line>  F5  A  0.05 </Line>
             <Line>  F6  A  0.0 </Line>

             <Line>  F1  B  0.025 </Line>
             <Line>  F2  B  0.90 </Line>
             <Line>  F3  B  0.025 </Line>
             <Line>  F4  B  0.0 </Line>
             <Line>  F5  B  0.0 </Line>
             <Line>  F6  B  0.05 </Line>

             <Line>  F1  C  0.0 </Line>
             <Line>  F2  C  0.05 </Line>
             <Line>  F3  C  0.90 </Line>
             <Line>  F4  C  0.05 </Line>
             <Line>  F5  C  0.0 </Line>
             <Line>  F6  C  0.0 </Line>

             <Line>  F1  D  0.0 </Line>
             <Line>  F2  D  0.0 </Line>
             <Line>  F3  D  0.05 </Line>
             <Line>  F4  D  0.95 </Line>
             <Line>  F5  D  0.0 </Line>
             <Line>  F6  D  0.0 </Line>
         </CondProbMatrix>
     </FaciesProbTrend>
 </APS_prob_trend>
 Comments to the model file specification:
 When specifying probabilities, there are one line per conditioned probability where the first name in the line
 is the facies name to be modelled, and the second name is the name of the category in in input discrete facies parameter.
 The third entry is the probability. The command UseConstantProbFromVolumeFraction is set to 1 if the user
 wants the average probability as output in each cell instead of the specified probability.
 The command SelectedZones define zone number for the zone this model is  defined for.
 If more than one zone can use the same specification, multiple zone numbers can be specified with a space
 in between in this command.
"""

from src.algorithms.defineFaciesProbTrend import DefineFaciesProb
from src.utils.methods import get_prefix, get_debug_level, get_model_file_name


def run(roxar=None, project=None, **kwargs):
    model_file_name = 'defineProbTrend.xml'
    print('Input model file: {}'.format(model_file_name))
    debug_level = get_debug_level(**kwargs)
    define_facies_trend = DefineFaciesProb(model_file_name, project, debug_level=debug_level)
    define_facies_trend.calculate_facies_probability_parameter()
    print('Finished running defineFaciesProbTrend')


if __name__ == "__main__":
    import roxar
    run(roxar, project)
