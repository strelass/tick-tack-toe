import datetime
import json
import time
import urllib

import redis
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.httpclient

from django.conf import settings
from importlib import import_module
from django.contrib.auth.models import User
import tornadoredis
from tick_tack_toe.models import Thread, Game
from tick_tack_toe.utils import start_game

session_engine = import_module(settings.SESSION_ENGINE)

c = tornadoredis.Client(host=settings.SESSION_REDIS_HOST, port=settings.SESSION_REDIS_PORT)
c.connect()


class MessagesHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def __init__(self, *args, **kwargs):
        super(MessagesHandler, self).__init__(*args, **kwargs)
        self.client = tornadoredis.Client(
            host=settings.SESSION_REDIS_HOST,
            port=settings.SESSION_REDIS_PORT
        )
        self.client.connect()

    def open(self, thread_id):
        session_key = self.get_cookie(settings.SESSION_COOKIE_NAME)
        session = session_engine.SessionStore(session_key)
        try:
            self.user_id = session["_auth_user_id"]
            self.sender_name = User.objects.get(id=self.user_id).username
        except (KeyError, User.DoesNotExist):
            self.close()
            return
        if not Thread.objects.filter(
                id=thread_id,
                participants__id=self.user_id
        ).exists():
            self.close()
            return
        self.channel = "".join(['thread_', thread_id, '_messages'])
        self.client.subscribe(self.channel)
        self.thread_id = thread_id
        self.client.listen(self.show_new_message)

    def handle_request(self, response):
        pass

    def on_message(self, message):
        if not message:
            return
        if len(message) > 10000:
            return
        c.publish(self.channel, json.dumps({
            "timestamp": int(time.time()),
            "sender": self.sender_name,
            "text": message,
        }))
        http_client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            "".join([
                settings.SEND_MESSAGE_API_URL,
                "/",
                self.thread_id,
                "/"
            ]),
            method="POST",
            body=urllib.urlencode({
                "message": message.encode("utf-8"),
                "api_key": settings.API_KEY,
                "sender_id": self.user_id,
            })
        )
        http_client.fetch(request, self.handle_request)

    def show_new_message(self, result):
        self.write_message(str(result.body))

    def on_close(self):
        try:
            self.client.unsubscribe(self.channel)
        except AttributeError:
            pass

        def check():
            if self.client.connection.in_progress:
                tornado.ioloop.IOLoop.instance().add_timeout(
                    datetime.timedelta(0.00001),
                    check
                )
            else:
                self.client.disconnect()

        tornado.ioloop.IOLoop.instance().add_timeout(
            datetime.timedelta(0.00001),
            check
        )


class GameHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def __init__(self, *args, **kwargs):
        super(GameHandler, self).__init__(*args, **kwargs)
        self.client = tornadoredis.Client(
            host=settings.SESSION_REDIS_HOST,
            port=settings.SESSION_REDIS_PORT
        )
        self.client.connect()

    def open(self, game_id):
        session_key = self.get_cookie(settings.SESSION_COOKIE_NAME)
        session = session_engine.SessionStore(session_key)
        try:
            self.user_id = session["_auth_user_id"]
            self.gamer_name = User.objects.get(id=self.user_id).username

        except (KeyError, User.DoesNotExist):
            self.close()
            return
        if not Game.objects.filter(
                id=game_id,
                participants__id=self.user_id
        ).exists():
            self.close()
            return

        self.channel = "".join(['thread_', game_id, '_game'])
        self.client.subscribe(self.channel)
        self.game_id = game_id
        self.client.listen(self.show_new_moves)

        # Makes the game start
        game = Game.objects.get(id=game_id)
        r = redis.StrictRedis()
        if game.status == "START":
            start_game(game_id, game.turn.id)
            r.hset(
                "".join(["thread_", game_id, "_game"]),
                "move_num",
                0
            )
        elif game.status == "IN_PROGRESS" and game.participants.\
                filter(id=self.user_id).exists():
            r.publish(
                "".join(["thread_", game_id, "_game"]), json.dumps({
                    "stat": "RESUME",
                    "turn": str(game.turn.id),
                }))

    def handle_request(self, response):
        pass

    def on_message(self, move):
        if not move:
            return
        if len(move) > 100:
            return
        http_client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            "".join([
                settings.MAKE_MOVE_API_URL,
                "/",
                self.game_id,
                "/"
            ]),
            method="POST",
            body=urllib.urlencode({
                "move": move,
                "api_key": settings.API_KEY,
                "gamer_id": self.user_id,
            })
        )
        http_client.fetch(request, self.handle_request)

    def show_new_moves(self, result):
        try:
            self.write_message(str(result.body))
        except:
            pass

    def on_close(self):
        try:
            c.publish(self.channel, json.dumps({
                "stat": "LEFT",
                "leaver": self.user_id,
            }))
        except:
            pass
        try:
            self.client.unsubscribe(self.channel)
        except AttributeError:
            pass

        def check():
            if self.client.connection.in_progress:
                tornado.ioloop.IOLoop.instance().add_timeout(
                    datetime.timedelta(0.00001),
                    check
                )
            else:
                self.client.disconnect()

        tornado.ioloop.IOLoop.instance().add_timeout(
            datetime.timedelta(0.00001),
            check
        )


application = tornado.web.Application([
    (r'/chat/(?P<thread_id>\d+)/', MessagesHandler),
    (r'/game/(?P<game_id>\d+)/', GameHandler),
])
