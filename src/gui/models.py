from peewee import *
from playhouse.sqlite_ext import JSONField, SqliteExtDatabase

from src.utils.constants import DataBase

db = SqliteExtDatabase(DataBase.NAME)


class BaseModel(Model):
    class Meta:
        database = db
