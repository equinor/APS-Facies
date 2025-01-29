# -*- coding: utf-8 -*-
from functools import total_ordering
from typing import Union, Dict, Generic, TypeVar, Optional, Callable, Any

from aps.utils.constants.simple import MinimumValues, MaximumValues, CrossSectionType
from aps.utils.types import Number

T = TypeVar('T')

Validator = Callable[[Any, float], bool]


def make_ranged_property(
    name: str,
    error_template: str,
    minimum: Optional[Number] = None,
    maximum: Optional[Number] = None,
    additional_validator: Optional[Validator] = None,
    show_given_value: bool = True,
    full_name: Optional[str] = None,
    strictly_less: bool = False,
    strictly_greater: bool = False,
) -> property:
    if additional_validator is None:

        def additional_validator(self, value):
            return True

    if full_name is None:
        full_name = name
    if minimum is None:
        minimum = MinimumValues[full_name]
    if maximum is None:
        maximum = MaximumValues[full_name]

    class Property:
        __slots__ = '_' + name

        def __init__(self):
            setattr(self, '_' + name, None)

        def get(self):
            return getattr(self, '_' + name)

        def set(self, value):
            if not isinstance(value, FmuProperty):
                try:
                    updatable = getattr(self, '_' + name).updatable
                except AttributeError:
                    updatable = False
                if isinstance(value, dict):
                    updatable = value['updatable']
                    value = value['value']
                    if value is None:
                        value = MinimumValues[name]
                value = FmuProperty(value, updatable)
            if is_between(
                value.value, minimum, maximum, strictly_less, strictly_greater
            ) and additional_validator(self, value):
                setattr(self, '_' + name, value)
            else:
                template = error_template
                if show_given_value:
                    template += '({value} was given)'
                raise ValueError(
                    template.format(
                        name=name,
                        min=minimum,
                        max=maximum,
                        value=value.value,
                        full_name=full_name,
                    )
                )

    return property(fget=Property.get, fset=Property.set)


def is_between(
    value: Number,
    _min: Number,
    _max: Number,
    strictly_less: bool = False,
    strictly_greater: bool = False,
) -> bool:
    return (
        _min < value < _max
        or _min == value
        and not strictly_greater
        or _max == value
        and not strictly_less
    )


def _make_simple_property(
    name: str, check: Callable[[Any, Any], bool], error_message: str
) -> property:
    class Property:
        __slots__ = '_' + name

        def __init__(self):
            setattr(self, '_' + name, None)

        def get(self):
            return getattr(self, '_' + name)

        def set(self, value):
            if check(self, value):
                setattr(self, '_' + name, value)
            else:
                raise ValueError(error_message)

    return property(fget=Property.get, fset=Property.set)


def make_trend_property(name: str) -> property:
    def is_model_and_rel_std_dev_set(self, value):
        if value:
            return self.model is not None and self.relative_std_dev is not None
        return True

    return _make_simple_property(
        name,
        is_model_and_rel_std_dev_set,
        'While trend is used, a trend model MUST be given, and the relative std.dev. must be given',
    )


def make_angle_property(
    name: str,
    full_name: Optional[str] = None,
    strictly_less: bool = False,
    strictly_greater: bool = False,
) -> property:
    if full_name is None:
        full_name = name
    return make_ranged_property(
        name,
        'The {full_name} angle MUST be between {min}°, and {max}°.',
        full_name=full_name,
        strictly_less=strictly_less,
        strictly_greater=strictly_greater,
    )


def make_lower_bounded_property(
    name: str,
    additional_validator: Optional[Validator] = None,
    full_name: Optional[str] = None,
    strictly_greater: bool = False,
) -> property:
    if strictly_greater:
        error_template = '{name} MUST be strictly greater than 0'
    else:
        error_template = '{name} MUST be greater than, or equal to 0'
    return make_ranged_property(
        name,
        error_template,
        additional_validator=additional_validator,
        full_name=full_name,
        strictly_greater=strictly_greater,
    )


@total_ordering
class FmuProperty(Generic[T]):
    __slots__ = 'value', 'updatable'

    def __init__(self, value: T, updatable: bool = False):
        assert isinstance(value, (int, float)) or value is None
        assert isinstance(updatable, bool)
        self.value = value
        self.updatable = updatable

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.value}, {self.updatable})'

    def __mul__(self, other: T) -> T:
        return self.value * other

    def __add__(self, other: T) -> T:
        return self.value + other

    def __sub__(self, other: T) -> T:
        return self.value - other

    def __abs__(self) -> T:
        return abs(self.value)

    def __eq__(self, other: Union['FmuProperty', Number]) -> bool:
        if isinstance(other, FmuProperty):
            return self.value == other.value and self.updatable == other.updatable
        return self.value == other

    def __lt__(self, other: Union['FmuProperty', Number]) -> bool:
        if isinstance(other, FmuProperty):
            other = other.value
        return self.value < other

    def __float__(self) -> float:
        return float(self.value)

    def __int__(self) -> int:
        return int(self.value)


class CrossSection:
    __slots__ = '_type', '_relative_position'

    types = CrossSectionType

    def __init__(
        self, type: Union[CrossSectionType, str], relative_position: float
    ) -> None:
        self._type = None
        self._relative_position = None
        if type not in CrossSectionType:
            raise ValueError(f'Invalid cross section: {type}')
        self._type = type
        self.relative_position = relative_position

    @property
    def type(self) -> CrossSectionType:
        return self._type

    @type.setter
    def type(self, value: Union[str, CrossSectionType]) -> None:
        if isinstance(value, str):
            try:
                value = CrossSectionType[value]
            except KeyError:
                raise ValueError(f'Invalid CrossSectionType ({value}')
        elif not isinstance(value, CrossSectionType):
            raise TypeError(
                f"Invalid argument {value}. Must be of type 'str', or 'CrossSectionType', not {type(value)}"
            )
        self._type = value

    @property
    def relative_position(self) -> float:
        return self._relative_position

    @relative_position.setter
    def relative_position(self, value: float):
        if not is_between(value, 0, 1):
            raise ValueError('The specified value must be in the interval [0.0, 1.0]')
        self._relative_position = value

    @classmethod
    def from_dict(cls, **kwargs: Dict[str, Union[str, float]]) -> 'CrossSection':
        type_ = kwargs['type']
        if isinstance(type_, str):
            type_ = CrossSectionType[type_]
        elif not (isinstance(type_, CrossSectionType)):
            ValueError(f'Unknown cross section type {type_}')
        return cls(type=type_, relative_position=kwargs.get('relativePosition', 0.5))
