#!/bin/env python
# -*- coding: utf-8 -*-
"""
Description:
    This script can be used to create binary (0/1) logs or probability logs from facies logs for blocked wells.
    The user specify which facies is to be used in APS modelling for each relevant zone. The script read
    the specified input facies log for the specified blocked well set. The algorithm is as follows to create
    probability logs:
    - For each blocked well grid cell, get the zone number from the zone log and the facies code from the facies log.
    - For each facies that is defined as modelling facies for a zone, the probability log is updated.
      Initially all blocked well cells are set to undefined. If the facies from the facies log is one of the
      modelling facies for the zone, assign probability value 1 to the probability log for that facies and assign 0
      to probability logs for the other modelling facies for the zone. If the facies is not one of the modelling facies
      for the zone, the probability log value is set to undefined.
      It is important to note that each zone may have different sets of modelling facies.
      If the user wants to model facies that is not observed and hence not found in the blocked well log,
      the facies can be specified to be a modelling facies. The probability log for the unobserved facies will get
      probability value 0 in all blocked well cells where other modelling facies is observed and undefined elsewhere.
      It is important to also include these unobserved facies in the list of modelling facies for the zone to ensure
      that these facies get 0 probability in blocked well grid cells.

    - The script has an option to use conditional probabilities which means that the probability
      P(modelling_facies | observed_facies) for the modelling facies in a blocked well grid cell given the observed
      facies can be specified to have any values betwwen 0 and 1. If the facies found in the facies log 
      is not one of the facies to be modelled for the zone, it will be treated as undefined.

    - This option is experimental and must be used with care, but can be a simple alternative
      if the interpretation is uncertain. Note however that each blocked well grid cell is treated independent from
      other blocked well grid cells and no spatial information about correlations are implemented in this simple model.
      The spatial correlations of facies between wells will depend on the APS model used.
      When using conditional probabilities, it is necessary to specify these for each modelled facies in each zone.
Input:
    Model file in xml format

    Example of model file format for a model creating binary probability logs:
    <?xml version="1.0" ?>
    <!-- This model specification is used in the script createProbabilityLogs.py 
         This example creates probability logs with probability equal to 0 or 1 (binary logs) 
         This example show a case where number of modelling facies vary from zone to zone. 
         Assume that facies A, B, C, D are observed and found in the facies log, but not in every zone. 
         They may or may not be used as modelling facies depending on the zone. In this example facies E can
         be an additional facies to be modelled, but that is not observed in any wells. The probability facies 
         for facies E will then get 0 as value within zone 5 in this example and missing code in all other zones.
         
         The output blocked well probability logs that appear within the RMS project after running 
         with this model file will have 0 or 1 for the facies specified to be modelling facies in a zone 
         and missing values for all the facies that is not specified as being modelling facies for a zone 
         The probability logs will have a name starting with the specified output prefix and will have 
         the facies name as a part of the log name. 
         The probability logs should be used in e.g. petrosim module in RMS together with 
         probability trend parameters to create 3D probability parameters conditioned to these logs.
         Note that it is important to be consistent and use the same set of modelled facies for a given zone
         when:
          1. Creating probability logs
          2. Creating probability trends
          3. Creating conditioned probability parameters in e.g petrosim
          4. When specifying APS model using the APSGUI plugin in RMS.   
         Inconsistent definition of which facies is modelling facies will result 
         in wrong conditioning and wrong normalization of the final probability parameters to be used in APS. -->

    <ProbLogs>
      <GridModelName>GridModelFine</GridModelName>
      <BlockedWells> BW  </BlockedWells>
      <FaciesLogName> Deterministic_facies </FaciesLogName>
      <ZoneLogName>   Zone  </ZoneLogName>
      <OutputPrefix> Prob_example1 </OutputPrefix>
      <ModellingFaciesPerZone>
        <Zone number="1">  A B C D </Zone>
        <Zone number="4">    B C D </Zone>
        <Zone number="5">  A   C D E </Zone>
        <Zone number="6">  A B     </Zone>
      </ModellingFaciesPerZone>
      <UseConditionalProbabilities> 0 </UseConditionalProbabilities>
    </ProbLogs>



    Example of model file format for a model using conditional probabilities:

    <?xml version="1.0" ?>
    <!-- This model specification is used in the script createProbabilityLogs.py 
         This example creates probability logs with probability between 0 and 1 
         The number of modelled facies may vary from zone to zone 
         Remember that the specified conditional probabilites must be normalized 
         The keyword <UseConditionalProbabilities> is set to 1 and it is necessary to
         specify probability for facies to be modelled for each facies in the facies log.
         The keyword <CondProbMatrix> can be specified with or without the attribute number which is zone number.
         If the keyword is specified without the attribute number, it means that the specified 
         conditional probabilities is common for all zones. In this case the number and name of modelled facies
         must be the same for all zones that are specified in keyword <ModellingFaciesPerZone>. IN the example below
         the number of facies to be modelled vary from zone to zone and <CondProbMatrix number="X"> 
         is specified for each zone number X. Each line defined by keyword <Line> define the conditional probability 
         for modelled facies given observed facies P(modelled_facies | observed_facies). The first facies name is
         the modelled facies (specified in keyword <Zone number="X"> in <ModellingFaciesPerZone>) while the second 
         is the observed facies (from the facies log). It is up to the user what the modelled facies is called, 
         but the observed facies must be the facies in the facies log. 
         Note that it is necessary to specify a probability for modelled facies for each observed facies in the log. --> 

    <ProbLogs>
      <GridModelName>GridModelFine</GridModelName>
      <BlockedWells> BW  </BlockedWells>
      <FaciesLogName> Deterministic_facies </FaciesLogName>
      <ZoneLogName>   Zone  </ZoneLogName>
      <OutputPrefix> Prob_example2 </OutputPrefix>
      <ModellingFaciesPerZone>
       <Zone number="1">  A  B  C  D F5 </Zone> 
       <Zone number="2">  A  B  C       </Zone> 
       <Zone number="4">  A  B  C  D     </Zone>
       <Zone number="6">        C  D    </Zone>
      </ModellingFaciesPerZone>
      <UseConditionalProbabilities> 1 </UseConditionalProbabilities>
      <CondProbMatrix number="1">
        <Line>  A  A  1.0 </Line>
        <Line>  B  A  0.0 </Line>
        <Line>  C  A  0.0 </Line>
        <Line>  D  A  0.0 </Line>
        <Line>  F5  A  0.0 </Line>

        <Line>  A  B  0.0 </Line>
        <Line>  B  B  1.0 </Line>
        <Line>  C  B  0.0 </Line>
        <Line>  D  B  0.0 </Line>
        <Line>  F5  B  0.0 </Line>

        <Line>  A  C  0.0 </Line>
        <Line>  B  C  0.0 </Line>
        <Line>  C  C  1.0 </Line>
        <Line>  D  C  0.0 </Line>
        <Line>  F5  C  0.0 </Line>

        <Line>  A  D  0.0 </Line>
        <Line>  B  D  0.0 </Line>
        <Line>  C  D  0.0 </Line>
        <Line>  D  D  0.5 </Line>
        <Line>  F5  D  0.5 </Line>
      </CondProbMatrix>

      <CondProbMatrix number="2">
        <Line>  A  A  1.0 </Line>
        <Line>  B  A  0.0 </Line>
        <Line>  C  A  0.0 </Line>

        <Line>  A  B  0.0 </Line>
        <Line>  B  B  1.0 </Line>
        <Line>  C  B  0.0 </Line>

        <Line>  A  C  0.0 </Line>
        <Line>  B  C  0.0 </Line>
        <Line>  C  C  1.0 </Line>


        <Line>  A  D  0.5  </Line>
        <Line>  B  D  0.25 </Line>
        <Line>  C  D  0.25 </Line>
      </CondProbMatrix>

      <CondProbMatrix number="4">
        <Line>  A   A  0.9 </Line>
        <Line>  B   A  0.1 </Line>
        <Line>  C   A  0.0 </Line>
        <Line>  D   A  0.0 </Line>

        <Line>  A  B  0.1 </Line>
        <Line>  B  B  0.7 </Line>
        <Line>  C  B  0.2 </Line>
        <Line>  D  B  0.0 </Line>

        <Line>  A  C  0.25 </Line>
        <Line>  B  C  0.25 </Line>
        <Line>  C  C  0.50 </Line>
        <Line>  D  C  0.0 </Line>


        <Line>  A  D  0.1 </Line>
        <Line>  B  D  0.1 </Line>
        <Line>  C  D  0.1 </Line>
        <Line>  D  D  0.7 </Line>
      </CondProbMatrix>


      <CondProbMatrix number="6">
        <Line>  C  A  0.55 </Line>
        <Line>  D  A  0.450 </Line>

        <Line>  C  B  0.7 </Line>
        <Line>  D  B  0.3 </Line>

        <Line>  C  C  1.0 </Line>
        <Line>  D  C  0.0 </Line>

        <Line>  C  D  0.0 </Line>
        <Line>  D  D  1.0 </Line>
      </CondProbMatrix>

    </ProbLogs>


Output:
    New logs are created in the blocked well set with defined values for the probabilities for the grid cells containing
    facies to be modelled for each individual zone and undefined for other facies. All grid cells in the blocked well
    set where the zone is undefined or the input facies log is undefined will also get undefined values for the probabilities.
    The output probability logs will get the name  <prefix>_<modelling_facies_name>.
"""
import xml.etree.ElementTree as ET
from aps.utils.xmlUtils import getKeyword, getTextCommand, getIntCommand
from aps.utils.roxar.modifyBlockedWellData import createProbabilityLogs
from aps.utils.exceptions.xml import MissingKeyword
from aps.utils.methods import get_debug_level, get_specification_file, SpecificationType
from aps.utils.constants.simple import Debug


def run(roxar=None, project=None, **kwargs):
    model_file_name = get_specification_file(_type=SpecificationType.PROBABILITY_LOG, **kwargs)
    debug_level = get_debug_level(**kwargs)
    _file = read_model_file(model_file_name)
    assign_binary_probabilities = not _file.use_conditioned_probabilities
    if debug_level >= Debug.VERBOSE:
        print('Grid model: {}'.format(_file.grid_model_name))
        print('BW        : {}'.format(_file.blocked_wells_set_name))
        print('Facies log: {}'.format(_file.facies_log_name))
        print('Zone   log: {}'.format(_file.zone_log_name))
        print('Prefix    : {}'.format(_file.prefix_probability_logs))
        print('Binary log: {}'.format(assign_binary_probabilities))
        print('Modelling facies:')
        print(_file.facies_list_per_zone)
        print('Conditional prob:')
        print(_file.conditional_prob_facies)

    realization_number = project.current_realisation
    if debug_level >= Debug.VERBOSE:
        print('Realization number: {}'.format(realization_number))

    # Case: assign_binary_probabilities = True
    # In this case the probabilities are either 1 or 0 or undefined.

    # Case: assign_binary_probabilities = False (NB: Experimental, not for use as default)
    # In this case the user must for each zone specify a probability for each modelled facies given the 
    # observed facies in the facies log.
    # The conditiona probabilities are specifed by one item per conditioned probability P(modelled_facies|observation_facies)
    # Note that the sum of probability for all modelled facies in a zone given an observed facies must be 1.0
    # The dictionary conditional_prob_facies as entries of the type  ('modelled_facies', 'observed_facies'):probability
    # and is the way to specify the conditional probability P('modelled_facies' | 'observed_facies').
    # Note that conditional probabilities must be specified for all observed facies in the log.
    # The modelled facies can be different in number and have different names compared with observed facies, 
    # but they can also have the same name.

    kwargs = dict(
        project=project,
        grid_model_name=_file.grid_model_name,
        bw_name=_file.blocked_wells_set_name,
        facies_log_name=_file.facies_log_name,
        zone_log_name=_file.zone_log_name,
        modelling_facies_per_zone=_file.facies_list_per_zone,
        prefix_prob_logs=_file.prefix_probability_logs,
        realization_number=realization_number,
    )
    if assign_binary_probabilities:
        print('Calculate probability logs as binary logs')

        createProbabilityLogs(**kwargs)
    else:
        print('Calculate probability logs using specified conditional probabilities:')
        if debug_level >= Debug.ON:
            for key, prob_value in _file.conditional_prob_facies.items():
                print('Zone: {}  Prob({}| {}) = {}'.format(key[0], key[1], key[2], prob_value))

        createProbabilityLogs(
            conditional_prob_facies=_file.conditional_prob_facies,
            **kwargs
        )

    print('Finished createProbabilityLogs')


def read_model_file(model_file_name):
    print(f'Read model file: {model_file_name}')
    root = ET.parse(model_file_name).getroot()
    main_keyword = 'ProbLogs'
    if root is None:
        raise MissingKeyword(main_keyword, model_file_name)

    kwargs = dict(parentKeyword=main_keyword, modelFile=model_file_name, required=True)
    keyword = 'GridModelName'
    grid_model_name = getTextCommand(root, keyword, **kwargs)

    keyword = 'BlockedWells'
    blocked_wells_name = getTextCommand(root, keyword, **kwargs)

    keyword = 'FaciesLogName'
    facies_log_name = getTextCommand(root, keyword, **kwargs)

    keyword = 'ZoneLogName'
    zone_log_name = getTextCommand(root, keyword, **kwargs)

    keyword = 'OutputPrefix'
    prefix = getTextCommand(root, keyword, **kwargs)

    keyword = 'UseConditionalProbabilities'
    use_conditioned_probabilities = getIntCommand(root, keyword, minValue=0, maxValue=1, defaultValue=0, **kwargs)

    keyword_facies = 'ModellingFaciesPerZone'
    facies_per_zone_obj = getKeyword(root, keyword_facies, **kwargs)
    facies_list_per_zone = {}
    if facies_per_zone_obj is None:
        raise ValueError(
            'Missing keyword {} in {}'.format(keyword_facies, model_file_name)
        )
    else:
        for zone_obj in facies_per_zone_obj.findall('Zone'):
            zone_number = int(zone_obj.get('number'))
            text = zone_obj.text
            words = text.split()
            facies_names = []
            for facies_name in words:
                facies_names.append(facies_name)
                facies_list_per_zone[zone_number] = facies_names
    
    
    conditional_prob_facies = {}
    if use_conditioned_probabilities:
        # Check if same facies is specified in all zones or not
        use_same_facies_in_all_zones = True
        zone_list = list(facies_list_per_zone.keys())
        facies_names_first_zone = list(facies_list_per_zone[zone_list[0]])
        for zone_number, facies_names in facies_list_per_zone.items():
            if len(facies_names_first_zone) != len(facies_names):
                use_same_facies_in_all_zones = False
            if zone_number != zone_list[0]:
                for f in facies_names:
                    if f not in facies_names_first_zone:
                        use_same_facies_in_all_zones = False


        keyword = 'CondProbMatrix'
        first = True
        common_cond_prob_matrix = False
        cond_prob_is_specified_for_zone = []

        for cond_prob_obj in root.findall(keyword):
            if not common_cond_prob_matrix:
                zone_number_string = cond_prob_obj.get('number')
                if zone_number_string is not None:
                    # In this case one cond prob matrix is specified per zone
                    zone_number = int(zone_number_string)
                    if zone_number in zone_list:
                        if zone_number in cond_prob_is_specified_for_zone:
                            # Cond prob matrix already read from model file
                            # Can not have two specification of the same cond prob matrix
                            raise KeyError(
                                'Keyword {} is specified multiple times for zone number {}'
                                ''.format(keyword, zone_number)
                            )
                        else:
                            # Add to list of specified cond prob matrices 
                            cond_prob_is_specified_for_zone.append(zone_number)
                    else:
                        raise KeyError(
                                'Zone number {} specified in keyword {} is not specified in keyword {}'
                                ''.format(zone_number, keyword, keyword_facies)
                            )

                    conditional_prob_facies = read_cond_prob_matrix(conditional_prob_facies,
                                                                    keyword, 
                                                                    keyword_facies, 
                                                                    cond_prob_obj, 
                                                                    facies_list_per_zone,
                                                                    zone_number,
                                                                    False)
                    first = False
                else:
                    common_cond_prob_matrix = True
                    if first:
                        if not use_same_facies_in_all_zones:
                            raise KeyError(
                                'The modelled facied per zone vary from zone to zone.\n'
                                'In this case it is necessary to specify conditional probabilities for each zone.\n'
                                'Use the attribute \'number\' to specify zone number in keyword {}'
                                ''.format(keyword)
                            )  
                        conditional_prob_facies = read_cond_prob_matrix(conditional_prob_facies,
                                                                        keyword, 
                                                                        keyword_facies, 
                                                                        cond_prob_obj, 
                                                                        facies_list_per_zone)

                        first = False
                    else:
                        raise KeyError(
                            'Keyword {} can not be specified multiple times if the keyword attribute \'number\' is not specified.'
                            ''.format(keyword)
                        )
            else:
                raise KeyError(
                    'Keyword {} is already specified without attribute \'number\' so the keyword can not be specified multiple times.'
                    ''.format(keyword)
                )

        # Check that all specified zones have a specified conditional probability matrix if this is required
        if not common_cond_prob_matrix:
            missing_cond_prob = []
            for zone_number in zone_list:
                if zone_number not in cond_prob_is_specified_for_zone:
                    missing_cond_prob.append(zone_number)
                text = ''
            if len(missing_cond_prob) > 0:
                for i in missing_cond_prob:
                    text = text + ' ' + str(i)
                raise KeyError(
                    'The following zones does not have any specification of the keyword {}: {}'
                    ''.format(keyword, text)
                )
    return _ModelFile(
        grid_model_name,
        blocked_wells_name,
        facies_log_name,
        zone_log_name,
        prefix,
        use_conditioned_probabilities,
        facies_list_per_zone,
        conditional_prob_facies,
    )




def read_cond_prob_matrix(conditional_prob_facies, 
                          keyword_parent, 
                          keyword_facies, 
                          cond_prob_obj, 
                          facies_list_per_zone,
                          zone_number=None,
                          use_common_cond_prod_matrix=True):
    zone_list = []
    if use_common_cond_prod_matrix:
        zone_list = list(facies_list_per_zone.keys())
        zone_number = zone_list[0]
    facies_names_for_zone = list(facies_list_per_zone[zone_number])
    facies_names_conditioned_to = []
    for obj in cond_prob_obj.findall('Line'):
        text = obj.text
        words = text.split()
        facies_name = words[0]
        if facies_name not in facies_names_for_zone:
            if not use_common_cond_prod_matrix:
                raise KeyError(
                    'Zone number {} specified in keyword {} has facies name {} that is not defined in keyword {}'
                    ''.format(zone_number, keyword_parent, facies_name, keyword_facies)
                )
            else:
                raise KeyError(
                    'Keyword {} has facies name {} that is not defined in keyword {}'
                    ''.format(keyword_parent, facies_name, keyword_facies)
                )

        facies_name_conditioned = words[1]
        facies_names_conditioned_to.append(facies_name_conditioned)
        prob = float(words[2])
        if prob < 0.0 or prob > 1.0:
            if not use_common_cond_prod_matrix:
                raise ValueError(
                    'Probability value {} specified in {} for zone {} is not in interval [0,1]'
                    ''.format(prob, keyword_parent, zone_number)
                ) 
            else:
                raise ValueError(
                    'Probability value {} specified in {} is not in interval [0,1]'
                    ''.format(prob, keyword_parent)
                ) 
                
        if use_common_cond_prod_matrix:
            for zone_number in zone_list:
                key = (zone_number, facies_name, facies_name_conditioned)
                conditional_prob_facies[key] = prob
        else:
            key = (zone_number, facies_name, facies_name_conditioned)
            conditional_prob_facies[key] = prob


    # Check that all facies names specified to be modelled for the zone actually has a specified probability
    for facies_name_conditioned  in facies_names_conditioned_to:
        for facies_name in facies_names_for_zone:
            key = (zone_number, facies_name, facies_name_conditioned)
            if key not in conditional_prob_facies:
                if not use_common_cond_prod_matrix:
                    raise ValueError(
                        'No conditional probability is specified for facies {} in zone {} conditioned to interpreted facies {}'
                        ''.format(facies_name, zone_number, facies_name_conditioned)
                    )   
                else:
                    raise ValueError(
                        'No conditional probability is specified for facies {} conditioned to interpreted facies {}'
                        ''.format(facies_name, facies_name_conditioned)
                    )   
    return conditional_prob_facies


class _ModelFile:
    __slots__ = (
        'grid_model_name', 'blocked_wells_set_name', 'facies_log_name', 'zone_log_name', 'prefix_probability_logs',
        'use_conditioned_probabilities', 'facies_list_per_zone', 'conditional_prob_facies',
    )

    def __init__(
            self,
            grid_model_name,
            blocked_wells_name,
            facies_log_name,
            zone_log_name,
            prefix_probability_logs,
            use_conditioned_probabilities,
            facies_list_per_zone,
            conditional_prob_facies,
    ):
        self.grid_model_name = grid_model_name
        self.blocked_wells_set_name = blocked_wells_name
        self.facies_log_name = facies_log_name
        self.zone_log_name = zone_log_name
        self.prefix_probability_logs = prefix_probability_logs
        self.use_conditioned_probabilities = use_conditioned_probabilities
        self.facies_list_per_zone = facies_list_per_zone
        self.conditional_prob_facies = conditional_prob_facies


if __name__ == '__main__':
    import roxar

    run(roxar, project, debug_level=Debug.VERBOSE)
