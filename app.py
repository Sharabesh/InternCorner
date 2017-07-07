#!/usr/local/bin/python3
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.websocket
import os
import requests
import datetime
from bs4 import BeautifulSoup
from models import *
from playhouse.shortcuts import *


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
	@tornado.web.authenticated
	def get(self):
		self.render("templates/html/check-in.html", user=self.get_current_user())

class MyAccountHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		user = get_user(self.get_current_email())
		user.project = user.project if user.project else json.dumps({"title":""})

		self.render("templates/html/my-account.html", user=self.get_current_user(),data=model_to_dict(user))

class RegistrationHandler(BaseHandler):
	def get(self):
		self.render("templates/html/register.html",failure=0,user=self.get_current_user())

class EngageHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		self.render("templates/html/engage.html",user=self.get_current_user())

class AnalyticsHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		self.render("templates/html/analytics.html",user=self.get_current_user())

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
			update_streak_login(values.email)
			self.redirect("/")
		else:
			self.render("templates/html/login.html",failure=1,user=self.get_current_user())

class LoginHandlerExtEndpoint(BaseHandler):
	def post(self):
		username = self.get_body_argument("username")
		password = self.get_body_argument("password")
		values = login_user(username,password)
		output_dic = {}
		if values.count > 0:
			values = list(values)[0]
			#Never send plaintext passwords!
			output_dic["success"] = 1
			output_dic["username"] = values.email
		else:
			output_dic["success"] = 0
		self.write(json.dumps(output_dic))


class UserPageEndpoint(BaseHandler):
	def get(self):
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
			article_dict["time_posted"] = (item.time_posted).strftime("%x")
			output_lst.append(article_dict)
		self.write(json.dumps(output_lst))

class RandomPostsEndpoint(BaseHandler):
	def get(self):
		results = get_random_10()
		output_lst = []
		for item in results:
			article_dict = {}
			article_dict["author"] = item.author
			article_dict["likes"] = item.likes
			article_dict["id"] = item.post_id
			article_dict["feeling"] = item.feeling
			article_dict["content"] = item.content
			article_dict["title"] = item.title
			article_dict["time_posted"] = (item.time_posted).strftime("%x")
			output_lst.append(article_dict)
		self.write(json.dumps(output_lst))

class SearchHandler(BaseHandler):
	def get(self):
		query = self.get_argument("q")
		table = self.get_argument("req")
		start = self.get_query_argument("start",0)
		results = search(query,table,start)
		output_lst = []
		if table == "p":
			for item in results:
				article_dict = {}
				article_dict["author"] = item.author
				article_dict["likes"] = item.likes
				article_dict["id"] = item.post_id
				article_dict["feeling"] = item.feeling
				article_dict["content"] = item.content
				article_dict["title"] = item.title
				article_dict["time_posted"] = (item.time_posted).strftime("%x")
				output_lst.append(article_dict)
		else:
			for item in results:
				article_dict = {}
				article_dict["username"] = item.username
				article_dict["department"] = item.department
				article_dict["firstname"] = item.firstname
				article_dict["lastname"] = item.lastname
				article_dict["email"] = item.email
				article_dict["school"] = item.school
				article_dict["manager"] = item.manager
				output_lst.append(article_dict)
		self.write(json.dumps(output_lst))



class UserPostsEndpoint(BaseHandler):
	def get(self):
		recieved_email = self.get_argument("email","")
		if recieved_email:
			username = self.get_current_user()
			start = self.get_argument("start")
			results = get_user_posts(recieved_email,start)
		else:
			email = self.get_current_email()
			start = self.get_argument("start")
			results = get_user_posts(email,start)
		output_lst = []
		for item in results:
			article_dict = {}
			article_dict["author"] = item.author
			article_dict["likes"] = item.likes
			article_dict["id"] = item.post_id
			article_dict["feeling"] = item.feeling
			article_dict["content"] = item.content
			article_dict["title"] = item.title
			article_dict["time_posted"] = (item.time_posted).strftime("%x")
			output_lst.append(article_dict)
		self.write(json.dumps(output_lst))

class NewChartEndpoint(BaseHandler):
	def get(self):
		start_date = self.get_argument("start_date","")
		end_date = self.get_argument("end_date","")
		department = self.get_argument("department","")
		school = self.get_argument("school","")
		results = get_chart_posts(start_date=start_date, end_date=end_date,department=department,school=school)
		output_list = []
		for item in results:
			article_dict = {}
			article_dict["feeling"] = item.feeling
			article_dict["time_posted"] = (item.time_posted).strftime("%x")
			output_list.append(article_dict)
		self.write(json.dumps(output_list))


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
		feeling = self.get_body_argument("feeling")
		anon = self.get_body_argument("anon",default="false")
		title = self.get_body_argument("title",default="")
		message = self.get_body_argument("message",default="")
		output_list = []
		update_streak_post(user)
		try:
			create_post(anon,feeling,message,user,title)
			resultMessage = {}
			resultMessage["success"] = "true"
			output_list.append(resultMessage)
			self.write(json.dumps(output_list))
		except:
			resultMessage = {}
			resultMessage["success"] = "false"
			output_list.append(resultMessage)
			self.write(json.dumps(output_list))

class PostExtEndpoint(BaseHandler):
	def post(self):
		user = self.get_body_argument("username")
		print(user)
		feeling = self.get_body_argument("feeling")
		anon = self.get_body_argument("anon",default="false")
		title = self.get_body_argument("title",default="")
		message = self.get_body_argument("message",default="")
		output_list = []
		try:
			create_post(anon,feeling,message,user,title)
			resultMessage = {}
			resultMessage["success"] = "true"
			output_list.append(resultMessage)
			self.write(json.dumps(output_list))
		except:
			resultMessage = {}
			resultMessage["success"] = "false"
			output_list.append(resultMessage)
			self.write(json.dumps(output_list))

class ViewHandler(BaseHandler):
	def get(self):
		print("here")
		user_email = self.get_argument("email")
		user = get_user(user_email)
		self.render("templates/html/view.html", user=self.get_current_user(), data=model_to_dict(user))


class GetCookieEndpoint(BaseHandler):
	def post(self):
		output_list = []
		email = self.get_body_argument("email")
		self.set_secure_cookie("email",email)
		cookie = self.get_secure_cookie("email")
		message = {}
		message["email-cookie"] = cookie
		message["email-received"] = email
		output_list.append(message)
		self.write(json.dumps(output_list))

class UserDataHandler(BaseHandler):
	def post(self):
		school = self.get_body_argument("school")
		manager = self.get_body_argument("manager")
		project = self.get_body_argument("project")
		user = self.get_current_email()
		add_user_data(school,manager,project,user)

class LikeUpdateEndpoint(BaseHandler):
	def post(self):
		user = self.get_current_email()
		id = self.get_argument("vote_id")
		self.write(update_vote(user,id))


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
		(r"/my-account",MyAccountHandler),
		(r"/",IndexHandler),
		(r"/check-in",CheckInHandler),
		(r"/register",RegistrationHandler),
		(r"/login",LoginHandler),
		(r"/engage",EngageHandler),
		(r"/analytics",AnalyticsHandler),
		(r"/search",SearchHandler),
		(r"/view",ViewHandler),
		#ENDPOINTS
		(r"/newPost", PostEndpoint),
		(r"/newUser",NewUserEndpoint),
		(r"/logout",LogoutEndpoint),
		(r"/top",UserPageEndpoint),
		(r"/user_posts",UserPostsEndpoint),
		(r"/random",RandomPostsEndpoint),
		(r"/newChart",NewChartEndpoint),
		(r"/update-fields",UserDataHandler),
		(r"/get-cookie",GetCookieEndpoint),
		(r"/login-ext", LoginHandlerExtEndpoint),
		(r"/newPostExt", PostExtEndpoint),
		(r"/like",LikeUpdateEndpoint)
	], debug=True, **settings)


if __name__ == "__main__":
	app = make_app()
	http_server = tornado.httpserver.HTTPServer(app)
	try:
		port = int(os.environ.get("PORT",5000))
		http_server.listen(port)
	except:
		port = int(os.environ.get("PORT", 3000))
		http_server.listen(port)

	print("Running at localhost:" + str(port))
	tornado.ioloop.IOLoop.current().start()
