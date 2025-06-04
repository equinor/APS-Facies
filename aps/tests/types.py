from typing import Dict, List, NewType, Tuple, TypeAlias

FaciesTableType: TypeAlias = Dict[int, str]
FaciesListType: TypeAlias = NewType('FaciesListType', List[str])
GaussianFieldsListType: TypeAlias = NewType('GaussianFieldsListType', List[str])

OverlayGroupType: TypeAlias = List[
    Tuple[List[Tuple[str, str, float, float]], List[str]]
]
