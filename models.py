#!/usr/local/bin/python3
import peewee
import psycopg2
from playhouse import signals
import time
import os
from urllib.parse import urlparse
import playhouse
import hashlib
from playhouse.postgres_ext import *
import re
from functools import reduce
import json
import datetime
import operator

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
	school = CharField(null=True)
	firstname = CharField(null=True)
	lastname = CharField(null=True)
	email = CharField(null=True)
	manager = CharField(null=True)
	project = CharField(null=True)

	class Meta:
		db_table='user'

class Posts(BaseModel):
	post_id= peewee.PrimaryKeyField()
	content = CharField(null=True)
	author = CharField(null=True)
	userid = ForeignKeyField(User,to_field='uniqueid', db_column='userid')
	anonymous = BooleanField(null=True)
	feeling = IntegerField(null=True)
	title = CharField(null=True)
	time_posted = DateTimeField()

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
	return q

def create_post(anonymous,feeling,message,user,title):
	correct_userid = User.select().where(User.email == user).execute()
	correct_userid = list(correct_userid)[0]
	userid = correct_userid.uniqueid
	Posts.create(content=message,author=user,feeling=feeling,likes=0,userid=userid,anonymous=anonymous,title=title)
	return True

def register_user(firstname,lastname,username,email,password,department):
	if User.select().where((User.email == email)).execute().count == 0:
		hasher = hashlib.sha1()
		hasher.update(password.encode("utf-8"))
		password = hasher.hexdigest()
		User.create(firstname=firstname,lastname=lastname,username=username,email=email,password=password,department=department)
		return True
	return False

def top_4():
	q = Posts.select().order_by(SQL('likes').desc()).limit(4)
	return q.execute()

def get_user_posts(email,start):
	posts = Posts.select().join(User).where(User.email == email).offset(start).limit(5)
	return posts.execute()

def get_user(email):
	return list(User.select().where(User.email == email).execute())[0]


"""
For our purposes this should work, but we need to heavily optimize this
with any decent size user base
"""
def search(query,table,start):
	print("QUERY IS: " + query)
	print("TABLE IS: " + table)
	print("START IS: " + str(start))
	query = query.replace(" ","%")
	if table == "p":
		q = Match(Posts.content,query) | Match(Posts.author,query) | Match(Posts.title,query)
		return Posts.select().where(q).limit(10).offset(start).execute()
	else:
		q = Match(User.username,query) | \
			Match( User.department,query) | (User.firstname.contains(query)) | \
			(User.lastname.contains(query)) | Match(User.email,query) | \
			Match(User.school,query) | (User.manager.contains(query))
		return User.select().where(q).limit(10).offset(start).execute()

	#Search entire table


def get_random_10():
	q = Posts.select().order_by(fn.Random()).limit(10)
	return q.execute()

def add_user_data(school,manager,project,user):
	print("ran")
	query = User.update(school=school,manager=manager,project={"title":project}).where(User.email == user)
	query.execute()

def update_vote(user_email,id):
	user = get_user(user_email).uniqueid
	print(user)
	print(id)
	if Likes.select().where(Likes.user_like_id == user, Likes.post_like_id == id).count() > 0:
		return -1
	else:
		Likes.create(user_like_id=user,post_like_id=id)
		return 1



def get_chart_posts(**kargs):
	filters = []
	for i in kargs:
		if kargs[i] != "":
			if i == "department":
				filters.append((User.department == kargs[i]))
			if i == "school":
				filters.append((User.school == kargs[i]))
			if i == "start_date":
				filters.append((Posts.time_posted >= kargs[i]))
			if i == "end_date":
				filters.append((Posts.time_posted <= kargs[i]))
	q = Posts.select(Posts.feeling, Posts.time_posted).join(User).where((reduce(operator.and_, filters))).order_by(SQL('time_posted').asc())
	return q.execute()

def search_posts(query):
	match = Match(Posts.title,query) | Match(Posts.content,query) | Match(Posts.author,query)
	return Posts.select().where(match).limit(10).execute()
