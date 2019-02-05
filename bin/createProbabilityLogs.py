#!/bin/env python
# -*- coding: utf-8 -*-
"""
Description:
    This script can be used to create binary (0/1) logs or probability logs from facies logs for blocked wells.
    The user specify which facies is to be used in APS modelling for each relevant zone. The script read
    the specified input facies log for the specified blocked well set. The algorithm is as follows to create
    probability logs are defined:
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
      facies is not only 1 if observed and 0 if not observed and undefined if not modelling facies.
      This option is experimental and must be used with care, but can be a simple alternative
      if the interpretation is uncertain. Note however that each blocked well grid cell is treated independent from
      other blocked well grid cells and no spatial information about correlations are implemented in this simple model.
      The are also some practical restrictions since one in principle will need a full matrix of conditional
      probabilities for each zone. This is not implemented here so either this option can only be used for one zone
      at a time or all specified zones must have identical set of modelling facies.

Input:
    Model file in xml format

    Example of model file format:
    <?xml version="1.0" ?>
    <!-- This model specification is used in the script createProbabilityLogs.py -->

    <ProbLogs>
     <GridModelName>GridModelCoarse</GridModelName>
     <BlockedWells> BW  </BlockedWells>
     <FaciesLogName> Facies </FaciesLogName>
     <ZoneLogName>   Zone  </ZoneLogName>
     <OutputPrefix> Prob </OutputPrefix>
     <ModellingFaciesPerZone>
     <Zone number="1">  F1 F2 F3 F4 F5 F6 </Zone>
     <Zone number="2">  F1 F2 F3 F4 F5 F6 </Zone>
     <Zone number="3">  F1 F2 F3 F4 F5 F6 </Zone>
     <Zone number="4">  F1 F2 F3 F4 F5 F6 </Zone>
     </ModellingFaciesPerZone>
     <UseConditionalProbabilities> 0 </UseConditionalProbabilities>

     <!-- The following keyword CondProbMatrix define conditional probabilites for modelling facies given input interpreted facies -->
     <!-- It is only used when keyword UseConditionalProbabilities is set to 1 and not used if this is set to 0 -->
     <!-- In the example below for keyword CondProbMatrix, the input facies log has facies A, B, C, D. -->
     <!-- Since the modelling facies is F1, F2, F3, F4, F5, the output probabiliyt logs will be Prob_F1, Prob_F2 etc -->
     <CondProbMatrix>
      <Line>  F1  A  1.0 </Line>
      <Line>  F2  A  0.0 </Line>
      <Line>  F3  A  0.0 </Line>
      <Line>  F4  A  0.0 </Line>
      <Line>  F5  A  0.0 </Line>

      <Line>  F1  B  0.0 </Line>
      <Line>  F2  B  1.0 </Line>
      <Line>  F3  B  0.0 </Line>
      <Line>  F4  B  0.0 </Line>
      <Line>  F5  B  0.0 </Line>

      <Line>  F1  C  0.0 </Line>
      <Line>  F2  C  0.0 </Line>
      <Line>  F3  C  1.0 </Line>
      <Line>  F4  C  0.0 </Line>
      <Line>  F5  C  0.0 </Line>

      <Line>  F1  D  0.0 </Line>
      <Line>  F2  D  0.0 </Line>
      <Line>  F3  D  0.0 </Line>
      <Line>  F4  D  0.5 </Line>
      <Line>  F5  D  0.25 </Line>

     </CondProbMatrix>
    </ProbLogs>

    Note that the probability logs are only defined for facies which are defined to be modelled. For all other facies,
    the probability log value is undefined. The normalization of the probabilities take care of this and ensure
    that sum of probabilities is 1 for the facies chosen to be modelled. When running in standard mode where
    binary logs are calculated, the logs defined as modelling facies for a zone have values 1 or 0 and sum to 1.
    When running in non-standard mode (assign_binary_probabilities = False), conditional probabilities are specified.
    NOTE: If running in non-standard mode, only one zone can be specified since this script has only one definition
    of conditional probabilities. It might work also in the special case that modelled facies are the same
    for all specified zones. and in this case the same conditional probabilities are used for all zones.
    But it will fail if there are zones with different numbers of facies som that modelled facies set is not identical
    for all specified zones.

Output:
    New logs are created in the blocked well set with defined values for the probabilities for the grid cells containing
    facies to be modelled for each individual zone and undefined for other facies. All grid cells in the blocked well
    set where the zone is undefined or the input facies log is undefined will also get undefined for the probabilities.
    The output probability logs will get the name  <prefix>_<modelling_facies_name>.
"""
import xml.etree.ElementTree as ET
from src.utils.xmlUtils import getKeyword, getTextCommand, getIntCommand
from src.utils.roxar.modifyBlockedWellData import createProbabilityLogs
from src.utils.exceptions.xml import MissingKeyword
from src.utils.methods import get_debug_level, get_specification_file, SpecificationType
from src.utils.constants.simple import Debug


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
    # In this case the user must specify a probability for each modelled facies given the observed facies in the facies log.
    # The conditiona probabilities are specifed by one item per conditioned probability P(modelled_facies|observation_facies)
    # Note that the sum of probability for all modelled facies in a zone given an observed facies must be 1.0
    # The dictionary conditional_prob_facies as entries of the type  ('modelled_facies', 'observed_facies'):probability
    # and is the way to specify the conditional probability P('modelled_facies' | 'observed_facies').
    # Note that conditional probabilities must be specified for all observed facies in the log.
    # The modelled facies can be different in number and have different names compared with observed facies, but they can also have the same name.

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
        for key, prob_value in _file.conditional_prob_facies.items():
            print('Prob({}| {}) = {}'.format(key[0], key[1], prob_value))

        createProbabilityLogs(
            conditional_prob_facies=_file.conditional_prob_facies,
            **kwargs
        )

    print('Finished createProbabilityLogs')


def read_model_file(model_file_name):
    print('Read model file: ' + model_file_name)
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

    keyword = 'ModellingFaciesPerZone'
    facies_per_zone_obj = getKeyword(root, keyword, **kwargs)
    facies_list_per_zone = {}
    if facies_per_zone_obj is None:
        raise ValueError(
            'Missing keyword {} in {}'.format(keyword, model_file_name)
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
        keyword = 'CondProbMatrix'
        cond_prob_obj = getKeyword(root, keyword, **kwargs)
        for obj in cond_prob_obj.findall('Line'):
            text = obj.text
            words = text.split()
            facies_name = words[0]
            facies_name_conditioned = words[1]
            prob = float(words[2])
            key = (facies_name, facies_name_conditioned)
            conditional_prob_facies[key] = prob

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
