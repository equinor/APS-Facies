from src.utils.exceptions.base import ApsException


class ZoneException(ApsException):
    pass


class MissingConformityException(ZoneException):
    def __init__(self, zone):
        super().__init__(f'The zone, with code {zone.zone_number}, has not been assigned a value for its conformity')
