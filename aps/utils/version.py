from warnings import warn
from functools import total_ordering
from typing import Union


@total_ordering
class Version:
    def __init__(self, version: str):
        version = version.split('.')
        major, minor, patch = 0, 0, 0
        if len(version) >= 3:
            patch = version[2]
            if not patch.isnumeric():
                warn(
                    f'{self.__class__.__name__} does not support PEP 440 versioning, '
                    f'but only strict semantic (major[.minor[.patch]])'
                )
                _patch = ''
                for char in patch:
                    if char.isalpha():
                        break
                    _patch += char
                patch = _patch
            patch = int(patch)
        if len(version) >= 2:
            minor = int(version[1])
        if len(version) >= 1:
            major = int(version[0])

        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self):
        return f'{self.major}.{self.minor}.{self.patch}'

    def __lt__(self, other: Union['Version', str]) -> bool:
        if isinstance(other, str):
            other = Version(other)
        return self.as_tuple() < other.as_tuple()

    def __eq__(self, other: Union['Version', str]) -> bool:
        if isinstance(other, str):
            other = Version(other)
        return self.as_tuple() == other.as_tuple()

    def as_tuple(self):
        return self.major, self.minor, self.patch
