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
from mailer import *
from playhouse.shortcuts import *


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

    def get_current_email(self):
        return self.get_secure_cookie("email")

    def is_superuser(self):
        cookie = self.get_secure_cookie("superuser")  # Returns Byte string
        return True if cookie == ("True").encode() else False

    def get(self):
        self.set_header("Content-Type", "application/json")


class NotFoundHandler(tornado.web.ErrorHandler, BaseHandler):
    def write_error(self, status_code, **kwargs):
        self.set_status(404)
        self.render(
            "templates/html/404.html",
            user=self.get_current_user(),
            superuser=self.is_superuser())


class IndexHandler(BaseHandler):
    def get(self):
        self.render(
            "templates/html/index.html",
            message=0,
            user=self.get_current_user(),
            superuser=self.is_superuser())


class CheckInHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render(
            "templates/html/check-in.html",
            user=self.get_current_user(),
            superuser=self.is_superuser())


class MyAccountHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        try:
            user = get_user(self.get_current_email())
        except BaseException:
            self.clear_cookie("user")
            self.clear_cookie("email")
            self.clear_cookie("superuser")
            self.redirect("/login")
        user.project = user.project if user.project else json.dumps({
                                                                    "title": ""})

        self.render(
            "templates/html/my-account.html",
            user=self.get_current_user(),
            data=model_to_dict(user),
            superuser=self.is_superuser())


class RegistrationHandler(BaseHandler):
    def get(self):
        self.render(
            "templates/html/register.html",
            failure=0,
            user=self.get_current_user(),
            superuser=self.is_superuser())


class EngageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render(
            "templates/html/engage.html",
            user=self.get_current_user(),
            superuser=self.is_superuser())


class AnalyticsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render(
            "templates/html/analytics.html",
            user=self.get_current_user(),
            superuser=self.is_superuser())


class LoginHandler(BaseHandler):
    def get(self):
        self.render(
            "templates/html/login.html",
            message="",
            user=self.get_current_user(),
            superuser=self.is_superuser())

    def post(self):
        username = self.get_body_argument("username")
        password = self.get_body_argument("password")
        values = login_user(username, password)
        if values.count > 0:
            values = list(values)[0]
            self.set_secure_cookie("user", username)
            self.set_secure_cookie("email", values.email)
            self.set_secure_cookie("superuser", str(values.superuser))
            update_streak_login(values.email)
            self.redirect("/")
        else:
            message = "Invalid Credentials!"
            self.render(
                "templates/html/login.html",
                message=message,
                success=0,
                user=self.get_current_user(),
                superuser=self.is_superuser())


class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        superuser = self.is_superuser()
        if superuser:
            self.render(
                "templates/html/admin.html",
                user=self.get_current_user(),
                superuser=superuser)
        else:
            self.redirect("/")


class AdminPostsEndpoint(BaseHandler):
    def get(self):
        limit = self.get_argument("limit", 100)
        print(limit)
        results = get_admin_posts(limit)
        output_lst = []
        for item in results:
            article_dict = {}
            article_dict["author"] = item.author
            article_dict["likes"] = item.likes
            article_dict["id"] = item.post_id
            article_dict["feeling"] = item.feeling
            article_dict["content"] = item.content
            article_dict["title"] = item.title
            article_dict["time_posted"] = str((item.time_posted))
            output_lst.append(article_dict)
        self.write(json.dumps(output_lst))


class LoginHandlerExtEndpoint(BaseHandler):
    def post(self):
        username = self.get_body_argument("username")
        password = self.get_body_argument("password")
        values = login_user(username, password)
        output_dic = {}
        if values.count > 0:
            values = list(values)[0]
            # Never send plaintext passwords!
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


class TopStreaksEndpoint(BaseHandler):
    def get(self):
        results = topStreaks()
        output_list = []
        for item in results:
            article_dict = {}
            article_dict["firstname"] = item.firstname
            article_dict["lastname"] = item.lastname
            article_dict["streak"] = item.streak
            output_list.append(article_dict)
        self.write(json.dumps(output_list))


class DeletePostEndpoint(BaseHandler):
    def post(self):
        post_id = self.get_body_argument("post_id")
        results = delete_post(post_id)
        response = {"success": 0}
        if results:
            response["success"] = 1
        self.write(json.dumps(response))


class ExportDataEndpoint(BaseHandler):
    def post(self):
        print("Exporting data")
        link = export_all_data()
        print(link)
        response = {
            "success": 1,
            "link": link
        }
        self.write(json.dumps(response))


class MostLikesEndpoint(BaseHandler):
    def get(self):
        results = mostLikes()
        output_list = []
        for item in results:
            article_dict = {}
            article_dict["author"] = item.author
            article_dict["content"] = item.content
            article_dict["likes"] = item.likes
            output_list.append(article_dict)
        self.write(json.dumps(output_list))


class RandomPostsEndpoint(BaseHandler):
    def get(self):
        results = get_random_10()
        output_lst = []
        for item in results:
            article_dict = {}
            article_dict["author"] = item.firstname + " " + item.lastname
            article_dict["likes"] = item.likes
            article_dict["id"] = item.post_id
            article_dict["feeling"] = item.feeling
            article_dict["content"] = item.content
            article_dict["title"] = item.title
            article_dict["time_posted"] = str((item.time_posted))
            article_dict["email"] = item.email
            output_lst.append(article_dict)
        self.write(json.dumps(output_lst))


class SearchHandler(BaseHandler):
    def get(self):
        query = self.get_argument("q")
        table = self.get_argument("req")
        start = self.get_query_argument("start", 0)
        results = search(query, table, start)
        output_lst = []
        if table == "p":
            for item in results:
                article_dict = {}
                article_dict["author"] = item.firstname + " " + item.lastname
                article_dict["likes"] = item.likes
                article_dict["id"] = item.post_id
                article_dict["feeling"] = item.feeling
                article_dict["content"] = item.content
                article_dict["title"] = item.title
                article_dict["time_posted"] = str((item.time_posted))
                article_dict["email"] = item.email
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
        recieved_email = self.get_argument("email", "")
        if recieved_email:
            username = self.get_current_user()
            start = self.get_argument("start")
            results = get_user_posts(recieved_email, start)
        else:
            email = self.get_current_email()
            start = self.get_argument("start")
            results = get_user_posts(email, start)
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


class PostDayEndpoint(BaseHandler):
    def get(self):
        results = postOfDay()
        output_list = []
        for item in results:
            article_dict = {}
            article_dict["content"] = item.content
            article_dict["title"] = item.title
            article_dict["author"] = item.author
            output_list.append(article_dict)
        self.write(json.dumps(output_list))


class NewChartEndpoint(BaseHandler):
    def get(self):
        start_date = self.get_argument("start_date", "")
        end_date = self.get_argument("end_date", "")
        department = self.get_argument("department", "")
        school = self.get_argument("school", "")
        results = get_chart_posts(
            start_date=start_date,
            end_date=end_date,
            department=department,
            school=school)
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
        if register_user(first, last, username, email, password, department):
            self.set_secure_cookie("email", email)
            self.set_secure_cookie("user", username)
            self.redirect("/")
        else:
            self.render(
                "templates/html/register.html",
                failure=1,
                user=self.get_current_user(),
                superuser=self.is_superuser())


class PostEndpoint(BaseHandler):
    def post(self):
        user = self.get_current_email()
        print(user)
        feeling = self.get_body_argument("feeling")
        anon = self.get_body_argument("anon", default=False)
        title = self.get_body_argument("title", default="")
        message = self.get_body_argument("message", default="")
        output_list = []
        update_streak_post(user)
        try:
            create_post(anon, feeling, message, user, title)
            resultMessage = {}
            resultMessage["success"] = "true"
            output_list.append(resultMessage)
            self.write(json.dumps(output_list))
        except BaseException:
            resultMessage = {}
            resultMessage["success"] = "false"
            output_list.append(resultMessage)
            self.write(json.dumps(output_list))


class PostExtEndpoint(BaseHandler):
    def post(self):
        user = self.get_body_argument("username")
        feeling = self.get_body_argument("feeling")
        anon = self.get_body_argument("anon", default="false")
        title = self.get_body_argument("title", default="")
        message = self.get_body_argument("message", default="")
        output_list = []
        try:
            create_post(anon, feeling, message, user, title)
            resultMessage = {}
            resultMessage["success"] = "true"
            output_list.append(resultMessage)
            self.write(json.dumps(output_list))
        except BaseException:
            resultMessage = {}
            resultMessage["success"] = "false"
            output_list.append(resultMessage)
            self.write(json.dumps(output_list))


class ViewHandler(BaseHandler):
    def get(self):
        user_email = self.get_argument("email")
        user = get_user(user_email)
        self.render(
            "templates/html/view.html",
            user=self.get_current_user(),
            data=model_to_dict(user),
            superuser=self.is_superuser())


class ForgotPasswordHandler(BaseHandler):
    def get(self):
        self.render("templates/html/forgot_password.html",
                    user="", superuser=self.is_superuser())

    def post(self):
        self.render(
            "templates/html/login.html",
            message="An email has been sent to the address provided.",
            success=1,
            user=self.get_current_user(),
            superuser=self.is_superuser())
        user_email = self.get_body_argument("email", default="")
        if user_email and verify_user(user_email):
            token = create_reset(user_email)
            url = "https://interncorner.herokuapp.com/reset_password?token=" + token
            subject = "Password Reset"
            send_mail(user_email, subject, url)


class ResetPasswordHandler(BaseHandler):
    def get(self):
        token = self.get_argument("token", default="")
        get_email_by_token(token)
        email = get_email_by_token(token)
        if email:
            self.render("templates/html/reset_password.html",
                        email=email, user="", superuser=False)
        else:
            self.render("templates/html/404_Error.html")

    def post(self):
        email = self.get_body_argument("email", default="")
        password = self.get_body_argument("password", default="")
        if reset_password(email, password):
            message = "Password reset successful."
            self.render(
                "templates/html/login.html",
                message=message,
                success=1,
                user=self.get_current_user(),
                superuser=self.is_superuser())
        else:
            message = "Password reset was not successful."
            self.render(
                "templates/html/login.html",
                message=message,
                success=0,
                user=self.get_current_user(),
                superuser=self.is_superuser())


class GetCookieEndpoint(BaseHandler):
    def post(self):
        output_list = []
        email = self.get_body_argument("email")
        self.set_secure_cookie("email", email)
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
        add_user_data(school, manager, project, user)


class LikeUpdateEndpoint(BaseHandler):
    def post(self):
        user = self.get_current_email()
        id = self.get_argument("vote_id")
        self.write(str(update_vote(user, id)))


class LogoutEndpoint(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.clear_cookie("email")
        self.clear_cookie("superuser")
        self.redirect('/')


class AddAdminPostEndpoint(BaseHandler):
    def post(self):
        user = self.get_current_email()
        title = self.get_argument("title")
        content = self.get_argument("content")
        add_admin_post(title, content, user)


settings = {
    "login_url": "/login",
    "compress_reponse": True,
    "cookie_secret": "b'4rp+0kDTQ8m5wgZ7F2eRYg0NXlVoF0IYmL9Z2GrpUdA='",
    'default_handler_class': NotFoundHandler,
    'default_handler_args': dict(status_code=404),
    'xheaders': True,
    'protocol': 'https'
}


def make_app():
    return tornado.web.Application([
        (r"/static/(.*)", tornado.web.StaticFileHandler, {
            "path": os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        }),
        # Pages
        (r"/my-account", MyAccountHandler),
        (r"/", IndexHandler),
        (r"/check-in", CheckInHandler),
        (r"/register", RegistrationHandler),
        (r"/login", LoginHandler),
        (r"/engage", EngageHandler),
        (r"/analytics", AnalyticsHandler),
        (r"/search", SearchHandler),
        (r"/view", ViewHandler),
        (r"/admin", AdminHandler),
        # ENDPOINTS
        (r"/newPost", PostEndpoint),
        (r"/newUser", NewUserEndpoint),
        (r"/logout", LogoutEndpoint),
        (r"/top", UserPageEndpoint),
        (r"/user_posts", UserPostsEndpoint),
        (r"/random", RandomPostsEndpoint),
        (r"/newChart", NewChartEndpoint),
        (r"/update-fields", UserDataHandler),
        (r"/get-cookie", GetCookieEndpoint),
        (r"/login-ext", LoginHandlerExtEndpoint),
        (r"/newPostExt", PostExtEndpoint),
        (r"/like", LikeUpdateEndpoint),
        (r"/admin-posts", AdminPostsEndpoint),
        (r"/add-admin", AddAdminPostEndpoint),
        (r"/forgot_password", ForgotPasswordHandler),
        (r"/reset_password", ResetPasswordHandler),
        (r"/mostLikes", MostLikesEndpoint),
        (r"/postOfDay", PostDayEndpoint),
        (r"/topStreaks", TopStreaksEndpoint),
        (r"/deletePost", DeletePostEndpoint),
        (r"/exportData", ExportDataEndpoint),

    ], debug=True, **settings)


if __name__ == "__main__":
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app)
    try:
        port = int(os.environ.get("PORT", 5000))
        http_server.listen(port)
    except BaseException:
        port = int(os.environ.get("PORT", 3000))
        http_server.listen(port)

    print("Running at localhost:" + str(port))
    tornado.ioloop.IOLoop.current().start()
