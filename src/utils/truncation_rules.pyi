# -*- coding: utf-8 -*-
from enum import Enum
from typing import Union, List, Dict, Any

from src.algorithms.APSFaciesProb import FaciesName
from src.algorithms.APSMainFaciesTable import Facies


class TruncationType(Enum):
    CUBIC:                           str
    NON_CUBIC:                       str
    BAYFILL:                         str

class TruncationSpecification:
    type: TruncationType

    global_facies_table:             List[Facies]
    facies_in_zone:                  List[Facies]
    facies_in_rule:                  List[Facies]

    fields_in_zone:                  List[str]
    fields_in_rule:                  List[str]
    fields_in_background:            List[List[List[str]]]
    values:                          Dict
    probabilities:                   List[float]
    use_constant_parameters:         bool

    def __init__(
            self,
            _type:                   Union[str, TruncationType],
            facies_table:            Dict[str, List[Facies]],
            gaussian_fields:         Dict[str, Any],
            values:                  Dict[str, Any],
            probabilities:           Dict[str, float],
            use_constant_parameters: bool,
    ): ...
    @classmethod
    def from_dict(
            cls,
            specification:           Dict
    ) -> TruncationSpecification: ...

    @staticmethod
    def _get_facies_table(
            specification:           Dict
    ) -> Dict: ...

    @staticmethod
    def _get_facies_probabilities(
            specification:           Dict
    ) -> Dict[FaciesName, float]: ...

    @staticmethod
    def _get_gaussian_fields(
            specification:           Dict
    ) -> Dict: ...

def make_truncation_rule(
        specification:               Union[TruncationSpecification, Dict]
): ...
