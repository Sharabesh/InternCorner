#!/usr/local/bin/python3
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
	uniqueid = peewee.PrimaryKeyField()
	username = CharField(null=True)
	password = CharField(null=True)
	department = CharField(null=True)

	class Meta:
		db_table='user'

class Posts(BaseModel):
	post_id= peewee.PrimaryKeyField()
	content = CharField(null=True)
	likes = IntegerField(null=True)
	author = CharField(null=True)
	userid = ForeignKeyField(User,to_field='uniqueid', db_column='userid')

	class Meta:
		db_table='posts'

class Likes(BaseModel):
	user_like_id = ForeignKeyField(User,to_field='uniqueid', db_column='user_like_id')
	post_like_id = ForeignKeyField(Posts,to_field='post_id', db_column='post_like_id')

	class Meta:
		db_table='likes'
		primary_key = CompositeKey("user_like_id","post_like_id")




def create_post(project,anonymous,phone,message,user):
	pass
	#TODO: add this functionality
