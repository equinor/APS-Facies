# -*- coding: utf-8 -*-
from typing import TypeVar, Union, Optional, Callable, Generic, Any, Dict

from src.utils.constants.simple import CrossSectionType

T = TypeVar('T')
Number = Union[int, float]
Validator = Callable[[Any, float], bool]


def make_ranged_property(
        name:                   str,
        error_template:         str,
        minimum:                Optional[Number]    = None,
        maximum:                Optional[Number]    = None,
        additional_validator:   Optional[Validator] = None,
        show_given_value:       bool                = True,
        full_name:              Optional[str]       = None,
        strictly_less:          bool                = False,
        strictly_greater:       bool                = False,
) -> property: ...
def _make_simple_property(
        name: str,
        check: Callable[[Any, Any], bool],
        error_message: str
) -> property: ...
def _make_bounded_property(
        name:                 str,
        minimum:              Number,
        maximum:              Number,
        error_template:       str,
        additional_validator: Optional[Validator] = None,
) -> property: ...
def make_lower_bounded_property(
        name:                 str,
        additional_validator: Optional[Validator] = None,
        full_name:            Optional[str] = None,
        strictly_greater:     bool = False,
) -> property: ...
def make_trend_property(name: str) -> property: ...
def make_angle_property(
        name:               str,
        full_name:          Optional[str]   = None,
        strictly_less:      bool            = False,
        strictly_greater:   bool            = False,
) -> property: ...

def is_between(
        value: Number,
        _min: Number,
        _max: Number,
        strictly_less: bool = False,
        strictly_greater: bool = False
) -> bool: ...


class FmuProperty(Generic[T]):
    value: T
    updatable: bool
    def __init__(self, value: T, updatable: bool = False) -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def __mul__(self, other: Number) -> Number: ...
    def __add__(self, other: Number) -> Number: ...
    def __sub__(self) -> T: ...
    def __abs__(self) -> T: ...
    def __eq__(self, other: Union[FmuProperty, Number]) -> bool: ...


class CrossSection:
    _type: CrossSectionType
    _relative_position: float
    types: CrossSectionType
    def __init__(
            self,
            type: Union[CrossSectionType, str],
            relative_position: float
    ) -> None: ...

    @property
    def type(self) -> CrossSectionType: ...
    @type.setter
    def type(self, value: Union[str, CrossSectionType]) -> None: ...
    relative_position: float
    @classmethod
    def from_dict(cls, **kwargs: Dict[str, Union[str, float]]) -> CrossSection: ...

