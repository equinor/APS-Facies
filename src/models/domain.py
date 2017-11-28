from peewee import *

from src.models.fields.enum import DebugField, ModeField
from src.utils.constants.simple import OperationalMode

db = SqliteDatabase('state.db')


class BaseModel(Model):
    class Meta:
        database = db


class RMSGridModel(BaseModel):
    pass


class APSModel(BaseModel):
    _mode = ModeField()
    grid_model_name = TextField(null=True, unique=True)  # TODO: Must be given when mode is 'NORMAL'
    zone_parameter_name = TextField(null=True, unique=True)  # TODO: Must be given when mode is 'NORMAL'
    region_parameter_name = TextField(null=True, unique=True)  # TODO: Must be given when mode is 'NORMAL'
    result_facies_parameter_name = TextField(null=True, unique=True)  # TODO: Must be given when mode is 'NORMAL'
    optimization_level = IntegerField(default=-1)
    debug_level = DebugField()

    # TODO: Take a look on 'mode dependent Fields'; create a new TextField that may be configured / depend on 'mode'

    _must_be_set_in_normal_mode = [
        grid_model_name, zone_parameter_name,
        region_parameter_name, result_facies_parameter_name
    ]

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if value not in OperationalMode:
            assert value in OperationalMode
        if value == OperationalMode.NORMAL:
            for item in self._must_be_set_in_normal_mode:
                # TODO: Do proper
                assert item is not None
        self._mode = value


class Zone(BaseModel):
    model = ForeignKeyField(APSModel, related_name='zones')
    zone_number = IntegerField(primary_key=True, null=False, unique=True, constraints=[Check('zone_number > 0')])
    use_constant_probability = BooleanField(default=True)
    simulation_box_thickness = FloatField(null=True)  # TODO: Must be set if trends are used


class Region(BaseModel):
    region_number = IntegerField(primary_key=True, null=False, unique=True)


class ZoneRegion(BaseModel):
    # FIXME: Note: Until regions are properly implemented, each zone will have exactly ONE region (dummy),
    # and every region will belong to exactly ONE zone.
    zone = ForeignKeyField(Zone)
    region = ForeignKeyField(Region)


class Facies(BaseModel):
    pass


class GridSize(BaseModel):
    zone = ForeignKeyField(Zone, primary_key=True)
    # TODO: Add default values
    x = IntegerField()
    y = IntegerField()
    z = IntegerField(null=True)  # TODO: Must be given when mode is 'NORMAL'
