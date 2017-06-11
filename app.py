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
	def get(self):
		self.set_header("Content-Type", "application/json")


class NewHandler(BaseHandler):
	def get(self):
		self.render("templates/html/index.html", message=0)

class CheckInHandler(BaseHandler):
	def get(self):
		self.render("templates/html/check-in.html")
class RegistrationHandler(BaseHandler):
	def get(self):
		self.render("templates/html/register.html")

class LoginHandler(BaseHandler):
	def get(self):
		self.render("templates/html/login.html")



class PostEndPoint(BaseHandler):
	def post(self):
		user = self.get_current_user()
		project = self.get_body_argument("project")
		anonymous = self.get_body_argument("anon")
		phone = self.get_body_argument("phone")
		message = self.get_body_argument("message")
		create_post(project,anonymous,phone,message)
		self.render("/",message=1)


settings = {
	"login_url":"/login",
	"compress_reponse":True,
	"cookie_secret":"private_key"
}


def make_app():
	return tornado.web.Application([
		(r"/static/(.*)", tornado.web.StaticFileHandler, {
			"path":os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
		}),
		(r"/",NewHandler),
		(r"/check-in",CheckInHandler),
		(r"/register",RegistrationHandler),
		(r"/login",LoginHandler),

		#ENDPOINTS
		(r"/newPost", PostEndPoint),
	], debug=True,compress_response=True, **settings)


if __name__ == "__main__":
	app = make_app()
	http_server = tornado.httpserver.HTTPServer(app)
	port = int(os.environ.get("PORT",5000))
	http_server.listen(port)
	print("Running at localhost:5000")
	tornado.ioloop.IOLoop.current().start()



