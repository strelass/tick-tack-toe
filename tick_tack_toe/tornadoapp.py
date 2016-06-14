import datetime
import json
import re
import urllib
import brukva

import redis
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.httpclient

from django.conf import settings
from importlib import import_module
from django.contrib.auth.models import User
from tick_tack_toe.models import Game
from tick_tack_toe.utils import start_game, join_game

session_engine = import_module(settings.SESSION_ENGINE)


class GameHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def __init__(self, *args, **kwargs):
        super(GameHandler, self).__init__(*args, **kwargs)
        self.client = brukva.Client(
            # host=settings.SESSION_REDIS_HOST,
            # port=int(settings.SESSION_REDIS_PORT)
        )
        self.client.connect()

    def open(self, game_id):
        session_key = self.get_cookie(settings.SESSION_COOKIE_NAME)
        session = session_engine.SessionStore(session_key)
        try:
            self.gamer_id = session["_auth_user_id"]
            self.gamer_name = User.objects.get(id=self.gamer_id).username

        except (KeyError, User.DoesNotExist):
            self.close()
            return

        self.channel = "".join(['thread_', game_id, '_game'])
        self.client.subscribe(self.channel)
        self.game_id = game_id
        self.client.listen(self.show_new_moves)

        # Makes the game start
        game = Game.objects.get(id=game_id)
        r = redis.StrictRedis()
        r.publish(
            "".join(["thread_", game_id, "_game"]), json.dumps({
                "stat": "CONNECTED",
                "gamer_id": self.gamer_id,
                "gamer_name": self.gamer_name,
            }))
        self.write_message(json.dumps({
                "stat": "GAME_STATUS",
                "game_status": game.status,
                "turn": str(game.turn.id),
                "winner": str(game.winner.id) if (game.status == "WINNER") else "",
            }))

    def handle_request(self, response):
        pass

    def on_message(self, move):
        if not move:
            return
        if len(move) > 1000 or not re.match("%(MOVE|MESS|HERE)%.*", move):
            return
        http_client = tornado.httpclient.AsyncHTTPClient()
        if move[1:5] == "MOVE":
            request = tornado.httpclient.HTTPRequest(
                "".join([
                    settings.MAKE_MOVE_API_URL,
                    "/",
                    self.game_id,
                    "/"
                ]),
                method="POST",
                body=urllib.urlencode({
                    "move": move[6:],
                    "api_key": settings.API_KEY,
                    "gamer_id": self.gamer_id,
                })
            )
        elif move[1:5] == "HERE":
            r = redis.StrictRedis()
            r.publish(
                "".join(["thread_", self.game_id, "_game"]), json.dumps({
                    "stat": "HANDSHAKE",
                    "gamer_id": str(self.gamer_id),
                    "gamer_name": self.gamer_name,
                }))
            return
        else:
            # move[1:5] == "MESS"
            r = redis.StrictRedis()
            r.publish(
                "".join(["thread_", self.game_id, "_game"]), json.dumps({
                    "stat": "MESSAGE",
                    "message": move[6:],
                    "user": self.gamer_name
                }))
            return
        http_client.fetch(request, self.handle_request)

    def show_new_moves(self, result):
        try:
            self.write_message(str(result.body))
        except:
            pass

    def on_close(self):
        try:
            r = redis.StrictRedis()
            r.publish(self.channel, json.dumps({
                "stat": "LEFT",
                "leaver": self.gamer_id,
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
    (r'/game/(?P<game_id>\d+)/', GameHandler),
])
