#!/usr/local/bin/python3
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.websocket
import os
import requests
from bs4 import BeautifulSoup
from models import *


class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie("user")
	def get_current_email(self):
		return self.get_secure_cookie("email")
	def get(self):
		self.set_header("Content-Type", "application/json")


class IndexHandler(BaseHandler):
	def get(self):
		self.render("templates/html/index.html", message=0, user=self.get_current_user())

class CheckInHandler(BaseHandler):
	def get(self):
		self.render("templates/html/check-in.html",user=self.get_current_user())

class MyAccountHandler(BaseHandler):
	def get(self):
		self.render("templates/html/my-account.html",user=self.get_current_user())

class RegistrationHandler(BaseHandler):
	def get(self):
		self.render("templates/html/register.html",failure=0,user=self.get_current_user())


class LoginHandler(BaseHandler):
	def get(self):
		self.render("templates/html/login.html",failure=0,user=self.get_current_user())
	def post(self):
		username = self.get_body_argument("username")
		password = self.get_body_argument("password")
		values = login_user(username,password)
		if values.count > 0:
			values = list(values)[0]
			self.set_secure_cookie("user",username)
			self.set_secure_cookie("email",values.email)
			print("redirecting")
			self.render("templates/html/index.html", message=0, user=self.get_current_user())
		else:
			self.redirect("/register")
			# self.render("templates/html/login.html",failure=1,user=self.get_current_user())

class UserPageEndpoint(BaseHandler):
	def get(self):
		full_dict = {}
		results = top_4()
		output_lst = []
		for item in results:
			article_dict = {}
			article_dict["author"] = item.author
			article_dict["likes"] = item.likes
			article_dict["id"] = item.post_id
			article_dict["feeling"] = item.feeling
			article_dict["content"] = item.content
			article_dict["title"] = item.title
			output_lst.append(article_dict)
		self.write(json.dumps(output_lst))

class UserPostsEndpoint(BaseHandler):
	def get(self):
		username = self.get_current_user()
		results = get_user_posts(username)
		output_lst = []
		for item in results:
			article_dict = {}
			article_dict["author"] = item.author
			article_dict["likes"] = item.likes
			article_dict["id"] = item.post_id
			article_dict["feeling"] = item.feeling
			article_dict["content"] = item.content
			article_dict["title"] = item.title
			output_lst.append(article_dict)
		self.write(json.dumps(output_lst))




class NewUserEndpoint(BaseHandler):
	def post(self):
		first = self.get_body_argument("first")
		last = self.get_body_argument("last")
		email = self.get_body_argument("email")
		department = self.get_body_argument("department")
		username = self.get_body_argument("username")
		password = self.get_body_argument("password")
		if register_user(first,last,username,email,password,department):
			self.set_secure_cookie("email",email)
			self.set_secure_cookie("user",username)
			self.redirect("/")
		else:
			self.render("templates/html/register.html",failure=1,user=self.get_current_user())

class PostEndpoint(BaseHandler):
	def post(self):
		user = self.get_current_email()
		print(user)
		project = self.get_body_argument("project")
		anonymous = self.get_body_argument("anon")
		doing_well = self.get_body_argument("phone")
		message = self.get_body_argument("message")
		title = self.get_body_argument("title")
		try:
			create_post(project,anonymous,doing_well,message,user,title)
			self.render("templates/html/index.html",message=0,user=self.get_current_user())
		except:
			self.render("templates/html/index.html", message=1, user=self.get_current_user())


class LogoutEndpoint(BaseHandler):
	def get(self):
		self.clear_cookie("user")
		self.clear_cookie("email")
		self.redirect('/')

settings = {
	"login_url":"/login",
	"compress_reponse":True,
	"cookie_secret":"b'4rp+0kDTQ8m5wgZ7F2eRYg0NXlVoF0IYmL9Z2GrpUdA='"
}


def make_app():
	return tornado.web.Application([
		(r"/static/(.*)", tornado.web.StaticFileHandler, {
			"path":os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
		}),
    #Pages
		(r"/check-in",CheckInHandler),
		(r"/my-account",MyAccountHandler),
		(r"/",IndexHandler),
		(r"/check-in",CheckInHandler),
		(r"/register",RegistrationHandler),
		(r"/login",LoginHandler),
		#ENDPOINTS
		(r"/newPost", PostEndpoint),
		(r"/newUser",NewUserEndpoint),
		(r"/logout",LogoutEndpoint),
		(r"/top",UserPageEndpoint),
		(r"/user_posts",UserPostsEndpoint)

	], debug=True,compress_response=True, **settings)


if __name__ == "__main__":
	app = make_app()
	http_server = tornado.httpserver.HTTPServer(app)
	port = int(os.environ.get("PORT",5000))
	http_server.listen(port)
	print("Running at localhost:5000")
	tornado.ioloop.IOLoop.current().start()
