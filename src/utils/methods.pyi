# -*- coding: utf-8 -*-
from enum import Enum
from typing import Dict, TypeVar, Optional, Set, List, Type, overload
from xml.etree.ElementTree import Element

T = TypeVar('T')
U = TypeVar('U')


def invert_dict(to_be_inverted: Dict[T, U]) -> Dict[U, T]: ...

@overload
def get_legal_values_of_enum(enum: Enum) -> Set[object]: ...

@overload
def get_legal_values_of_enum(enum: Type[Enum]) -> Set[object]: ...

@overload
def get_printable_legal_values_of_enum(enum: Enum) -> List[str]: ...

@overload
def get_printable_legal_values_of_enum(enum: Type[Enum]) -> List[str]: ...

@overload
def get_item_from_model_file(tree: Element, model_file_name: Optional[str]) -> str: ...

@overload
def get_item_from_model_file(tree: Element, keyword: str, model_file_name: Optional[str]) -> str: ...

def get_selected_zones(tree: Element, keyword: str, model_file: Optional[str]) -> List[int]: ...

@overload
def get_colors(n: int, min_colors: int) -> List[str]: ...

@overload
def get_colors(n: int) -> List[str]: ...
