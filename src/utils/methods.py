from typing import Dict, TypeVar

T = TypeVar('T')
U = TypeVar('U')


def invert_dict(to_be_inverted: Dict[T, U]) -> Dict[U, T]:
    return {
        to_be_inverted[key]: key for key in to_be_inverted.keys()
    }
