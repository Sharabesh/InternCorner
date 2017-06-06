#!/usr/bin/python
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.websocket
import os
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append(".")
from models import *


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
    def get(self):
        self.set_header("Content-Type", "application/json")

class MainHandler(BaseHandler):
    def get(self):
        self.render("templates/html/main.html")

class NewHandler(BaseHandler):
    def get(self):
        self.render("templates/html/index.html")

class CheckInHandler(BaseHandler):
    def get(self):
        self.render("templates/html/check-in.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("Opened Socket")
    def on_message(self,message):
        print(message)
        to_search = message.replace(" ","+")
        goog_search = "https://www.google.co.uk/search?sclient=psy-ab&client=ubuntu&hs=k5b&channel=fs&biw=1366&bih=648&noj=1&q=" + to_search
        r = requests.get(goog_search)
        soup = BeautifulSoup(r.text, "html.parser")
        first_link = soup.find('cite').text
        self.write_message("First Google Result Was: " + first_link)
    def on_close(self):
        print("Closed Socket")



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
        (r"/websocket",WebSocketHandler),
        (r"/main",MainHandler),
        (r"/check-in",CheckInHandler)

    ], debug=True,compress_response=True, **settings)


if __name__ == "__main__":
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app)
    port = int(os.environ.get("PORT",5000))
    http_server.listen(port)
    print("Running at localhost:5000")
    tornado.ioloop.IOLoop.current().start()



