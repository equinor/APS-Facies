from datetime import datetime
from peewee import *
from playhouse.sqlite_ext import JSONField, SqliteExtDatabase

from src.utils.constants import DataBase

db = SqliteExtDatabase(DataBase.NAME)


class BaseModel(Model):
    class Meta:
        database = db


class MetaData(BaseModel):
    key = TextField(unique=True, index=True, null=False)
    value = TextField(unique=False, null=True)  # TODO: Is a textfield sufficient?


class TimeStamp(BaseModel):
    time_stamp = DateTimeField(default=datetime.now())


class Zone(BaseModel):
    pass


class Region(BaseModel):
    pass


class Facies(BaseModel):
    pass


class GaussianRandomField(BaseModel):
    pass
