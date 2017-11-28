from enum import Enum
from typing import NewType, Type, Optional

from peewee import Field

from src.utils.constants.simple import Debug, OperationalMode, VariogramType

T = NewType('T', Enum)


class EnumField(Field):
    db_field = 'int'

    def __init__(self, enum_type: Type[T], default=None):
        super().__init__(default=default)
        self._enum_type = enum_type
        assert default is None or isinstance(default, enum_type)
        self._default_value = default

    def db_value(self, value: T) -> int:
        return value.value

    def python_value(self, value: int) -> Optional[T]:
        try:
            return self._enum_type(value)
        except ValueError:
            return self._default_value


class DebugField(EnumField):
    def __init__(self, default=Debug.OFF):
        super().__init__(Debug, default=default)


class ModeField(EnumField):
    def __init__(self, default=OperationalMode.EXPERIMENTAL):
        assert default in OperationalMode
        super().__init__(OperationalMode, default=default)


class VariogramField(EnumField):
    def __init__(self, default=VariogramType.SPHERICAL):
        assert default in VariogramType
        super().__init__(VariogramType, default=default)
