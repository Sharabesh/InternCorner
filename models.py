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
from datetime import datetime

url = urlparse(os.environ["DATABASE_URL"])

config = dict(
	database=url.path[1:],
	user=url.username,
	password=url.password,
	host=url.hostname,
	port=url.port,
	sslmode='require'
)

conn = PostgresqlExtDatabase(autocommit=True, autorollback=True, register_hstore=False, **config)


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
	streak = IntegerField(null=True)
	streak_date = DateTimeField()
	superuser = BooleanField(null=True)

	class Meta:
		db_table = 'user'


class Posts(BaseModel):
	post_id= peewee.PrimaryKeyField()
	content = CharField(null=True)
	author = CharField(null=True)
	userid = ForeignKeyField(User,to_field='uniqueid', db_column='userid')
	anonymous = BooleanField(null=True)
	feeling = IntegerField(null=True)
	title = CharField(null=True)
	likes = IntegerField(null=True)
	time_posted = DateTimeField()
	admin = BooleanField(null=True)

	class Meta:
		db_table = 'posts'

class Resets(BaseModel):
	email = CharField(null=False, primary_key=True)
	token = CharField(null=False)
	timestamp = DateTimeField();

	class Meta:
		db_table = 'resets'


class Likes(BaseModel):
	user_like_id = ForeignKeyField(User, to_field='uniqueid', db_column='user_like_id')
	post_like_id = ForeignKeyField(Posts, to_field='post_id', db_column='post_like_id')

	class Meta:
		db_table = 'likes'
		primary_key = CompositeKey("user_like_id", "post_like_id")

def login_user(username,password):
	hasher = hashlib.sha1()
	hasher.update(password.encode("utf-8"))
	password = hasher.hexdigest()
	q = User.select().where((User.username == username) & (User.password == password)).execute()
	return q

def create_post(anonymous,feeling,message,user,title,admin=False):
	correct_userid = User.select(User.uniqueid).where(User.email == user).execute()
	correct_userid = list(correct_userid)[0]
	userid = correct_userid.uniqueid
	Posts.create(content=message,author=user,feeling=feeling,likes=0,userid=userid,anonymous=anonymous,title=title,admin=admin)
	return True

def update_streak_post(user):
	correct_user = User.select(User.uniqueid, User.streak, User.streak_date).where(User.email == user).execute()
	correct_user = list(correct_user)[0]
	userid = correct_user.uniqueid
	new_streak = correct_user.streak
	diff = days_between(str(correct_user.streak_date), str(datetime.now().strftime("%Y-%m-%d")))
	if diff == 1:
		new_streak = correct_user.streak + 1
	elif diff > 1:
		new_streak = 0
	new_date = str(datetime.now().strftime("%Y-%m-%d"))
	User.update(streak=new_streak, streak_date=new_date).where(User.email == user).execute()


def update_streak_login(user):
	correct_user = User.select(User.uniqueid, User.streak_date).where(User.email == user).execute()
	correct_user = list(correct_user)[0]
	userid = correct_user.uniqueid
	diff = days_between(str(correct_user.streak_date), str(datetime.now().strftime("%Y-%m-%d")))
	if diff > 1:
		User.update(streak=0).where(User.email == user).execute()


def days_between(d1, d2):
	d1 = datetime.strptime(d1, "%Y-%m-%d")
	d2 = datetime.strptime(d2, "%Y-%m-%d")
	return abs((d2 - d1).days)


def register_user(firstname, lastname, username, email, password, department):
	if User.select().where((User.email == email)).execute().count == 0:
		hasher = hashlib.sha1()
		hasher.update(password.encode("utf-8"))
		password = hasher.hexdigest()
		User.create(firstname=firstname, lastname=lastname, username=username, email=email, password=password,
					department=department)
		return True
	return False

def verify_user(email):
	if User.select().where(User.email == email).execute().count == 1:
		return True
	else:
		return False

def top_4():
	q = Posts.select().order_by(SQL('likes').desc()).limit(4)
	return q.execute()


def get_user_posts(email, start):
	posts = Posts.select().join(User).where(User.email == email).offset(start).limit(5)
	return posts.execute()

def get_user(email):
	return list(User.select().where(User.email == email).execute())[0]




"""
For our purposes this should work, but we need to heavily optimize this
with any decent size user base
"""

# Search entire table
def search(query, table, start):
    query = query.replace(" ", "%")
    if table == "p":
        q = Match(Posts.content, query) | Match(Posts.author, query) | Match(Posts.title, query)
        return Posts.select(Posts, User).join(User).where(q).limit(10).offset(start).naive().execute()
    else:
        q = Match(User.username, query) | \
            Match(User.department, query) | (User.firstname.contains(query)) | \
            (User.lastname.contains(query)) | Match(User.email, query) | \
            Match(User.school, query) | (User.manager.contains(query))
        return User.select().where(q).limit(10).offset(start).execute()





def get_random_10():
	q = Posts.select(Posts,User).join(User).where(Posts.content != "").order_by(fn.Random()).limit(10).naive()
	return q.execute()

def add_user_data(school, manager, project, user):
	print("ran")
	query = User.update(school=school, manager=manager, project={"title": project}).where(User.email == user)
	query.execute()

def update_vote(user_email,id):
	user = get_user(user_email).uniqueid
	if Likes.select().where(Likes.user_like_id == user, Likes.post_like_id == id).count() > 0:
		Posts.update(likes=Posts.likes - 1).where(Posts.post_id == id).execute()
		Likes.delete().where(Likes.post_like_id == id).execute()  # Remove user from likes table
		return -1
	else:
		Likes.create(user_like_id=user,post_like_id=id)
		Posts.update(likes=Posts.likes + 1).where(Posts.post_id == id).execute()
		return 1

def get_admin_posts():
	posts = Posts.select().where(Posts.admin == True).execute()
	return posts

def add_admin_post(title,content,user):
	correct_userid = User.select(User.uniqueid).where(User.email == user).execute()
	correct_userid = list(correct_userid)[0]
	userid = correct_userid.uniqueid
	Posts.create(content=content, author=user, feeling=0, likes=0, userid=userid, anonymous=False,
				 title=title,admin=True)
	return True

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
	q = Posts.select(Posts.feeling, Posts.time_posted).join(User).where((reduce(operator.and_, filters))).order_by(
		SQL('time_posted').asc())
	return q.execute()


def search_posts(query):
	match = Match(Posts.title, query) | Match(Posts.content, query) | Match(Posts.author, query)
	return Posts.select().where(match).limit(10).execute()

#Delete all old reset entries related to email, create new reset entry
def create_reset(email):
	Resets.delete().where(Resets.email == email).execute()
	hasher = hashlib.sha1()
	hasher.update(email.encode("utf-8"))
	token = hasher.hexdigest()
	Resets.create(email=email, token=token, timestamp=datetime.now())
	return token

def get_email_by_token(token):
	if Resets.select().where((Resets.token == token)).execute().count > 0:
		results = Resets.select().where(Resets.token == token).limit(1).execute()
		return (list(results)[0]).email
	else:
		return False

#Delete all old reset entries. Reset user passsword
def reset_password(email, password):
	Resets.delete().where(Resets.email == email).execute()
	hasher = hashlib.sha1()
	hasher.update(password.encode("utf-8"))
	password = hasher.hexdigest()
	User.update(password=password).where(User.email == email).execute()
	return True
