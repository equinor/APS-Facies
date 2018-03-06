from enum import Enum
from typing import Dict, TypeVar, Optional, Set, List, Type, Union

from src.utils.exceptions.xml import MissingKeyword

from copy import copy

T = TypeVar('T')
U = TypeVar('U')


def invert_dict(to_be_inverted: Dict[T, U]) -> Dict[U, T]:
    return {
        to_be_inverted[key]: key for key in to_be_inverted.keys()
    }


def get_legal_values_of_enum(enum: Union[Type[Enum], Enum]) -> Optional[Set[object]]:
    if isinstance(enum, Enum):
        return {v.value for v in enum.__members__.values()}
    return None


def get_printable_legal_values_of_enum(enum: Union[Type[Enum], Enum]) -> List[str]:
    legal_values = get_legal_values_of_enum(enum)
    if legal_values:
        return [str(values) for values in legal_values]
    return ['']


def get_item_from_model_file(tree, keyword, model_file_name=None):
    item = tree.find(keyword)
    if item is not None:
        text = item.text.strip()
        return copy(text.strip())
    else:
        raise MissingKeyword(keyword, model_file_name)


def get_selected_zones(tree, model_file=None, keyword='SelectedZones'):
    selected_zone_numbers = []
    zones = []
    obj = tree.find(keyword)
    if obj is not None:
        texts = obj.text.split()
        for s in texts:
            zones.append(int(s.strip()))
        for i in range(len(zones)):
            zone_number = zones[i]
            # Zone numbers are specified from 1, but need them numbered from 0
            selected_zone_numbers.append(zone_number - 1)
        return selected_zone_numbers
    else:
        raise MissingKeyword(keyword, model_file)


def get_colors(n: int, min_colors: int = 2) -> List[str]:
    """
    :param n: The number of colors / facies
    :type n: int
    :param min_colors: The minimum number of colors needed. Default 2
    :type min_colors: int
    :return: List of colors
    :rtype: List[str]
    """
    colors = [
        'lawngreen', 'grey', 'dodgerblue', 'gold', 'darkorchid', 'cyan', 'firebrick',
        'olivedrab', 'blue', 'crimson', 'darkorange', 'red',
    ]
    if min_colors <= n <= len(colors):
        return colors[:n]
    else:
        return []
