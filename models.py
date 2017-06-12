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

from peewee import DateTimeField, CharField, IntegerField, BooleanField


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
	firstname = CharField(null=True)
	lastname = CharField(null=True)
	email = CharField(null=True)

	class Meta:
		db_table='user'

class Posts(BaseModel):
	post_id= peewee.PrimaryKeyField()
	content = CharField(null=True)
	likes = IntegerField(null=True)
	author = CharField(null=True)
	userid = ForeignKeyField(User,to_field='uniqueid', db_column='userid')
	anonymous = BooleanField(null=True)

	class Meta:
		db_table='posts'

class Likes(BaseModel):
	user_like_id = ForeignKeyField(User,to_field='uniqueid', db_column='user_like_id')
	post_like_id = ForeignKeyField(Posts,to_field='post_id', db_column='post_like_id')

	class Meta:
		db_table='likes'
		primary_key = CompositeKey("user_like_id","post_like_id")

def login_user(username,password):
	hasher = hashlib.sha1()
	hasher.update(password.encode("utf-8"))
	password = hasher.hexdigest()
	q = User.select().where((User.username == username) & (User.password == password)).execute()
	if q.count == 0:
		return False
	else:
		return q

def create_post(project,anonymous,phone,message,user):
	correct_userid = User.select().where(User.email == user).execute()
	correct_userid = list(correct_userid)[0]
	userid = correct_userid.uniqueid
	Posts.create(content=message,author=user,likes=0,userid=userid,anonymous=anonymous)

def register_user(firstname,lastname,username,email,password,department):
	if User.select().where((User.email == email)).execute().count == 0:
		hasher = hashlib.sha1()
		hasher.update(password.encode("utf-8"))
		password = hasher.hexdigest()
		User.create(firstname=firstname,lastname=lastname,username=username,email=email,password=password,department=department)
		return True
	return False



