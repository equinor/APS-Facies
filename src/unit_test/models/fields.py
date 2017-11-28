from unittest import TestCase
from playhouse.test_utils import test_database
from peewee import *

from src.models.fields.enum import DebugField

test_db = SqliteDatabase(':memory:')


class Table(Model):
    debug = DebugField()


class TestDebugField(TestCase):
    pass
