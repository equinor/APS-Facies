from typing import Union


class FmuAttribute:
    __slots__ = 'name', 'value'

    def __init__(self, name: str, value: Union[int, float]):
        self.name = name
        self.value = value
