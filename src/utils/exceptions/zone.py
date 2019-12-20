from src.utils.exceptions.base import ApsException


class ZoneException(ApsException):
    pass


class MissingConformityException(ZoneException):
    def __init__(self, zone):
        super().__init__(
            'The zone, with code {}, has not been assigned a value for its conformity'
            ''.format(zone.zone_number)
        )
