import peewee
import psycopg2
from playhouse import signals
import time
import peewee
import os
from urllib.parse import urlparse
import playhouse
import hashlib
from playhouse.postgres_ext import *
import re
from functools import reduce
import json

from peewee import DateTimeField, CharField, IntegerField

print(os.environ)
print("DATABASE_URL" in os.environ)
url = urlparse(os.environ["DATABASE_URL"])

config = dict(
	database = url.path[1:],
	user = url.username,
	password = url.password,
	host= url.hostname,
	port= url.port,
	sslmode = 'require'
)

conn = PostgresqlExtDatabase(autocommit= True, autorollback = True, register_hstore = False, **config)

class BaseModel(signals.Model):
	class Meta:
		database = conn

class User(BaseModel):
	uniqueid = peewee.PrimaryKeyField(null=True)
	username = CharField(null=True)
	password=CharField(null=True)
	department= CharField(null=True)
	posts = CharField(null=True)

	class Meta:
		db_table='user'