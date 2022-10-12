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
      facies can be specified to have any values between 0 and 1. If the facies found in the facies log
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
import os
from pathlib import Path
from aps.utils.xmlUtils import getKeyword, getTextCommand, getIntCommand
from aps.utils.ymlUtils import get_text_value, get_bool_value, get_dict, readYml
from aps.utils.roxar.modifyBlockedWellData import createProbabilityLogs
from aps.utils.exceptions.xml import MissingKeyword
from aps.utils.constants.simple import Debug
from aps.utils.methods import check_missing_keywords_list, get_cond_prob_dict

def run(params):
    """
        Create probability logs from facies logs.
        Usage alternatives:
        - Specify a dictionary with model file name containing all input information. See example 1.
        - Specify a dictionary with all input information. See example 2.

Example 1:

from aps.toolbox import create_probability_logs
from aps.utils.constants.simple import Debug

input_dict ={
    'project': project,
    'model_file_name': "test_prob_logs1.xml",
    'debug_level': Debug.VERBOSE,
}
create_probability_logs.run(input_dict)


Example 2:

from aps.toolbox import create_probability_logs
from aps.utils.constants.simple import Debug


# Define input parameters

# Modelled facies for each zone can vary from zone to zone
modelling_facies_dict = {
    1: ["F1", "F2", "F3"],
    2: ["F1", "F2", "F3"],
}
# Observed facies for zone 1 is A, B, C, D
# Observed facies for zone 2 is A, B, C
# Prob for modelled facies F1 is set to 1 where A is observed
# Prob for modelled facies F2 is set to 1 where B is observed
# Prob for modelled facies F3 is set to 1 where C is observed
# Where observed facies is D in zone 1 :
#   F1 is assigned prob = 0.7
#   F2 is assigned prob = 0.2
#   F3 is assigned prob = 0.1
conditional_prob_facies ={
    (1, "F1", "A"): 1.0,
    (1, "F2", "A"): 0.0,
    (1, "F3", "A"): 0.0,
    (1, "F1", "B"): 0.0,
    (1, "F2", "B"): 1.0,
    (1, "F3", "B"): 0.0,
    (1, "F1", "C"): 0.0,
    (1, "F2", "C"): 0.0,
    (1, "F3", "C"): 1.0,
    (1, "F1", "D"): 0.7,
    (1, "F2", "D"): 0.2,
    (1, "F3", "D"): 0.1,

    (2, "F1", "A"): 1.0,
    (2, "F2", "A"): 0.0,
    (2, "F3", "A"): 0.0,
    (2, "F1", "B"): 0.0,
    (2, "F2", "B"): 1.0,
    (2, "F3", "B"): 0.0,
    (2, "F1", "C"): 0.0,
    (2, "F2", "C"): 0.0,
    (2, "F3", "C"): 1.0,
}

input_dict = {
    "project":                   project,
    "debug_level":               Debug.VERBOSE,
    "grid_model_name":           "GridModelFine",
    "bw_name":                   "BW4",
    "facies_log_name":           "Facies",
    "zone_log_name":             "Zone",
    "modelling_facies_per_zone": modelling_facies_dict,
    "prefix_prob_logs":          "Prob",
    "conditional_prob_facies":   conditional_prob_facies,
}
create_probability_logs.run(input_dict)

    """
    project = params['project']
    debug_level = params.get('debug_level', Debug.OFF)
    model_file_name = params.get('model_file_name', None)
    use_cond_prob = False
    if model_file_name is not None:
        # Read model file and overwrite all model parameters
        _file = read_model_file(model_file_name)
        params.pop('model_file_name')
        params['grid_model_name'] = _file.grid_model_name
        params['bw_name'] = _file.blocked_wells_set_name
        params['facies_log_name'] = _file.facies_log_name
        params['zone_log_name'] = _file.zone_log_name
        params['modelling_facies_per_zone'] = _file.facies_list_per_zone
        params['prefix_prob_logs'] =_file.prefix_probability_logs
        params['realization_number'] = project.current_realisation
        use_cond_prob = _file.use_conditioned_probabilities

        # Optional parameters
        if use_cond_prob:
            kw = 'conditional_prob_facies'
            params[kw] = _file.conditional_prob_facies if use_cond_prob else None
            if params[kw] is None:
                raise ValueError(f"Missing specification of: {kw}")
            conditional_prob_facies = params[kw]
    else:
        # Optional parameters
        conditional_prob_facies = params.get('conditional_prob_facies', None)
        if conditional_prob_facies is not None:
            use_cond_prob = True

    # Check that all necessary parameters are set
    keywords_required = [
            'project', 'grid_model_name','bw_name',
            'facies_log_name', 'zone_log_name', 'modelling_facies_per_zone',
            'prefix_prob_logs',
             ]
    check_missing_keywords_list(params, keywords_required)

    if debug_level >= Debug.VERBOSE:
        print(f"Realization number: {project.current_realisation}")
        print(f"Grid model: {params['grid_model_name']}")
        print(f"BW        : {params['bw_name']}")
        print(f"Facies log: {params['facies_log_name']}")
        print(f"Zone   log: {params['zone_log_name']}")
        print(f"Prefix    : {params['prefix_prob_logs']}")
        print(f"Binary log: {not use_cond_prob}")
        print(f"Modelling facies: {params['modelling_facies_per_zone']}")

    # Case: use_cond_prob == False
    # In this case the probabilities are either 1 or 0 or undefined.

    # Case: use_cond_prob == True (Note: This feature is experimental, not for use as default)
    # In this case the user must for each zone specify a probability for each modelled facies given the 
    # observed facies in the facies log.
    # The conditional probabilities are specifed by one item per conditioned probability
    #   P(modelled_facies|observation_facies)
    # Note that the sum of probability for all modelled facies in a zone given an observed facies must be 1.0
    # The dictionary conditional_prob_facies has entries of the type:
    #   key = (zone_number, 'modelled_facies', 'observed_facies') and value is probability
    # and is the way to specify the conditional probability P('modelled_facies' | 'observed_facies') for a given zone number.
    # Note that conditional probabilities must be specified for all observed facies in the log.
    # The modelled facies can be different in number and have different names compared with observed facies, 
    # but they can also have the same name and they may depend on zone number.
    if not use_cond_prob:
        print('Calculate probability logs as binary logs')
        createProbabilityLogs(**params)
    else:
        print('Calculate probability logs using specified conditional probabilities')
        if debug_level >= Debug.VERBOSE:
            sorted_by_zone_dict = dict(sorted(conditional_prob_facies.items(), key=lambda item: (item[0][0], item [0][2], item[0][1])))
            for key, prob_value in sorted_by_zone_dict.items():
                print(f'Zone: {key[0]}  Prob({key[1]}| {key[2]}) = {prob_value}')
        createProbabilityLogs(**params)

    print('Finished createProbabilityLogs')

def read_model_file(model_file_name):
    # Check suffix of file for file type
    model_file = Path(model_file_name)
    suffix = model_file.suffix.lower().strip('.')
    if suffix in ['yaml', 'yml']:
        _file = _read_model_file_yml(model_file_name)
    elif suffix == 'xml':
        _file = _read_model_file_xml(model_file_name)
    else:
        raise ValueError(f"Model file name: {model_file_name}  must be either 'xml' or 'yml' format")
    return _file

def _read_model_file_xml(model_file_name: str):
    assert model_file_name
    print(f'Read model file: {model_file_name}')
    if not os.path.exists(model_file_name):
        raise IOError(f"File {model_file_name} does not exist")

    root = ET.parse(model_file_name).getroot()
    main_keyword = 'ProbLogs'
    if root is None:
        raise MissingKeyword(main_keyword, model_file_name)

    kwargs = dict(parentKeyword=main_keyword, modelFile=model_file_name, required=True)
    grid_model_name = getTextCommand(root, 'GridModelName', **kwargs)
    blocked_wells_name = getTextCommand(root, 'BlockedWells', **kwargs)
    facies_log_name = getTextCommand(root, 'FaciesLogName', **kwargs)
    zone_log_name = getTextCommand(root, 'ZoneLogName', **kwargs)
    prefix = getTextCommand(root, 'OutputPrefix', **kwargs)
    use_conditioned_probabilities = getIntCommand(root, 'UseConditionalProbabilities',
        minValue=0, maxValue=1, defaultValue=0, **kwargs)

    keyword_facies = 'ModellingFaciesPerZone'
    facies_per_zone_obj = getKeyword(root, keyword_facies, **kwargs)
    facies_list_per_zone = {}
    if facies_per_zone_obj is None:
        raise ValueError(f"Missing keyword {keyword_facies} in {model_file_name}")

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
            if common_cond_prob_matrix:
                raise KeyError(
                    f"Keyword {keyword} is already specified without attribute 'number' "
                    "so the keyword can not be specified multiple times."
                )

            zone_number_string = cond_prob_obj.get('number')
            if zone_number_string is None:
                common_cond_prob_matrix = True
                if not first:
                    raise KeyError(
                        f"Keyword {keyword} can not be specified multiple times if the keyword attribute 'number' is not specified."
                    )

                if not use_same_facies_in_all_zones:
                    raise KeyError(
                        f"The modelled facied per zone vary from zone to zone.\n"
                        f"In this case it is necessary to specify conditional probabilities for each zone.\n"
                        f"Use the attribute 'number' to specify zone number in keyword {keyword}"
                    )
                conditional_prob_facies = _read_cond_prob_matrix(conditional_prob_facies,
                                                                keyword,
                                                                keyword_facies,
                                                                cond_prob_obj,
                                                                facies_list_per_zone)

                first = False
            else:
                # In this case one cond prob matrix is specified per zone
                zone_number = int(zone_number_string)
                if zone_number not in zone_list:
                    raise KeyError(
                        f"Zone number {zone_number} specified in keyword {keyword} "
                        f"is not specified in keyword {keyword_facies}"
                    )

                if zone_number in cond_prob_is_specified_for_zone:
                    # Cond prob matrix already read from model file
                    # Can not have two specification of the same cond prob matrix
                    raise KeyError(
                        f"Keyword {keyword} is specified multiple times for zone number {zone_number}"
                    )

                # Add to list of specified cond prob matrices
                cond_prob_is_specified_for_zone.append(zone_number)
                conditional_prob_facies = _read_cond_prob_matrix(conditional_prob_facies,
                                                                keyword,
                                                                keyword_facies,
                                                                cond_prob_obj,
                                                                facies_list_per_zone,
                                                                zone_number,
                                                                False)
                first = False

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
                    f"The following zones does not have any specification of the keyword {keyword}: {text}")

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

def _read_cond_prob_matrix(conditional_prob_facies,
                          keyword_parent,
                          keyword_facies,
                          cond_prob_obj,
                          facies_list_per_zone,
                          zone_number=None,
                          use_common_cond_prod_matrix=True):
    zone_list = []
    if use_common_cond_prod_matrix:
        zone_list = list(facies_list_per_zone.keys())
        if len(zone_list) == 0:
            raise ValueError("Facies per zone must be specified. Can not have 0 facies.")
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
                    f"Zone number {zone_number} specified in keyword {keyword_parent} has "
                    f"facies name {facies_name} that is not defined in keyword {keyword_facies}"
                )
            else:
                raise KeyError(
                    f"Keyword {keyword_parent} has facies name {facies_name} "
                    f"that is not defined in keyword {keyword_facies}"
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
                        f"No conditional probability is specified for facies {facies_name} "
                        f"in zone {zone_number} conditioned to interpreted facies {facies_name_conditioned}"
                    )   
                else:
                    raise ValueError(
                        f"No conditional probability is specified for facies {facies_name} "
                        f"conditioned to interpreted facies {facies_name_conditioned}"
                    )   
    return conditional_prob_facies

def _read_model_file_yml(model_file_name: str):
    print(f'Read model file: {model_file_name}')
    spec_all = readYml(model_file_name)

    kw_parent = 'ProbLogs'
    spec = spec_all[kw_parent] if kw_parent in spec_all else None
    if spec is None:
        raise ValueError(f"Missing keyword: {kw_parent} ")

    grid_model_name = get_text_value(spec, kw_parent, 'GridModelName')
    blocked_wells_name = get_text_value(spec, kw_parent, 'BlockedWells')
    facies_log_name = get_text_value(spec, kw_parent, 'FaciesLogName')
    zone_log_name = get_text_value(spec, kw_parent, 'ZoneLogName')
    prefix = get_text_value(spec, kw_parent, 'OutputPrefix')
    use_conditioned_probabilities = get_bool_value(spec, 'UseConditionalProbabilities', False)
    fac_dict = get_dict(spec, kw_parent, 'ModellingFaciesPerZone')
    facies_dict = {}
    for znr in fac_dict:
        # The text string contains multiple facies names
        facies_list = fac_dict[znr].split()
        facies_dict[znr]= facies_list

    # Check if all specified zones use the same set of modelling facies
    common_facies_list = True
    active_zone_list = list(facies_dict.keys())
    facies_list_previous_zone = facies_dict[active_zone_list[0]]
    for znr in active_zone_list:
        facies_list = facies_dict[znr]
        if facies_list != facies_list_previous_zone:
            common_facies_list = False

    conditional_prob_facies = {}
    if use_conditioned_probabilities:
        cond_table = get_dict(spec, kw_parent, 'CondProbMatrix')
        conditional_prob_facies = get_cond_prob_dict(cond_table, active_zone_list, common_facies_list=common_facies_list)

    return _ModelFile(
        grid_model_name,
        blocked_wells_name,
        facies_log_name,
        zone_log_name,
        prefix,
        use_conditioned_probabilities,
        facies_dict,
        conditional_prob_facies,
    )



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

