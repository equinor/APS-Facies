# -*- coding: utf-8 -*-
from src.utils.constants.simple import MinimumValues, MaximumValues
from src.utils.constants.simple import CrossSectionType


def make_ranged_property(name, error_template, minimum=None, maximum=None, additional_validator=None, show_given_value=True, full_name=None, strictly_less=False, strictly_greater=False):
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
            if (
                    is_between(value.value, minimum, maximum, strictly_less, strictly_greater)
                    and additional_validator(self, value)
            ):
                setattr(self, '_' + name, value)
            else:
                template = error_template
                if show_given_value:
                    template += '({value} was given)'
                raise ValueError(
                    template.format(name=name, min=minimum, max=maximum, value=value.value, full_name=full_name)
                )

    return property(fget=Property.get, fset=Property.set)


def is_between(value, _min, _max, strictly_less=False, strictly_greater=False):
    if (
            _min < value < _max
            or _min == value and not strictly_greater
            or _max == value and not strictly_less
    ):
        return True
    else:
        return False


def _make_simple_property(name, check, error_message):
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


def make_trend_property(name):
    def is_model_and_rel_std_dev_set(self, value):
        if value:
            return self.model is not None and self.relative_std_dev is not None
        return True

    return _make_simple_property(name, is_model_and_rel_std_dev_set, 'While trend is used, a trend model MUST be given, and the relative std.dev. must be given')


def make_angle_property(name, full_name=None, strictly_less=False, strictly_greater=False):
    if full_name is None:
        full_name = name
    return make_ranged_property(
        name,
        'The {full_name} angle MUST be between {min}°, and {max}°.',
        full_name=full_name,
        strictly_less=strictly_less,
        strictly_greater=strictly_greater
    )


def make_lower_bounded_property(name, additional_validator=None, full_name=None, strictly_greater=False):
    if strictly_greater:
        error_template = '{name} MUST be strictly greater than 0'
    else:
        error_template = '{name} MUST be greater than, or equal to 0'
    return make_ranged_property(
        name, error_template, additional_validator=additional_validator,
        full_name=full_name, strictly_greater=strictly_greater
    )


# TODO: Inherit from float / int ?
class FmuProperty:
    __slots__ = 'value', 'updatable'

    def __init__(self, value, updatable=False):
        assert isinstance(value, (int, float)) or value is None
        assert isinstance(updatable, bool)
        self.value = value
        self.updatable = updatable

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return '(' + str(self.value) + ', ' + str(self.updatable) + ')'

    def __mul__(self, other):
        return self.value * other

    def __add__(self, other):
        return self.value + other

    def __sub__(self, other):
        return other - self.value

    def __abs__(self):
        return abs(self.value)

    def __eq__(self, other):
        if isinstance(other, FmuProperty):
            return self.value == other.value and self.updatable == other.updatable
        return self.value == other


class CrossSection:
    __slots__ = '_type', '_relative_position'

    types = CrossSectionType

    def __init__(self, type, relative_position):
        self._type = None
        self._relative_position = None

        self.type = type
        self.relative_position = relative_position

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value not in CrossSectionType:
            value = CrossSectionType[value]
        self._type = value

    @property
    def relative_position(self):
        return self._relative_position

    @relative_position.setter
    def relative_position(self, value):
        if not is_between(value, 0, 1):
            raise ValueError(
                'The specified value must be in the interval [0.0, 1.0]'
            )
        self._relative_position = value

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(
            type=kwargs['type'],
            relative_position=kwargs.get('relativePosition', 0.5)
        )
