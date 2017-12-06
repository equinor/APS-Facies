from enum import Enum
from typing import Dict, TypeVar, Optional, Set, List, Type, Union

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
