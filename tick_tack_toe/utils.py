import json
import re
from django.http import HttpResponse

import redis

from django.utils import dateformat

from tick_tack_toe.models import Message, Move, Game


def json_response(obj):
    return HttpResponse(
        json.dumps(obj),
        content_type='application/json',
    )


def send_message(thread_id,
                 sender_id,
                 message_text,
                 sender_name=None):

    message = Message()
    message.text = message_text
    message.thread_id = thread_id
    message.sender_id = sender_id
    message.save()

    thread_id = str(thread_id)
    sender_id = str(sender_id)

    r = redis.StrictRedis()

    if sender_name:
        r.publish("".join(["thread_", thread_id, "_messages"]), json.dumps({
            "timestamp": dateformat.format(message.datetime, 'U'),
            "sender": sender_name,
            "text": message_text,
        }))

    for key in ("total_messages", "".join(["from_", sender_id])):
        r.hincrby(
            "".join(["thread_", thread_id, "_messages"]),
            key,
            1
        )


def join_game(game_id, username):
    game_id = str(game_id)
    r = redis.StrictRedis()
    r.publish("".join(["thread_", game_id, "_game"]), json.dumps({
        "stat": "JOIN",
        "newbie": username,
    }))


def try_to_make_move(game, move, gamer):
    if gamer not in game.participants.all():
        return {"error": "Dont do this!."}
    if not re.match("^\d+:\d+$", move):
        return {"error": "Wrong move format."}

    x = int(move.split(":")[0])
    y = int(move.split(":")[1])
    if not (0 <= x < game.sizeX and 0 <= y < game.sizeY):
        return {"error": "Wrong move format."}

#   TODO:  Checking our rools
    if game.move_set.filter(x=x, y=y).exists():
        return {"error": "This field is already occupied."}
    return {
        "x": x,
        "y": y,
    }


def make_move(game_id,
              gamer_id,
              x,
              y):

    game = Game.objects.get(id=game_id)
    game_id = str(game_id)
    r = redis.StrictRedis()

    num = r.hget(
        "".join(["thread_", game_id, "_game"]),
        "move_num"
    )
    r.hincrby(
        "".join(["thread_", game_id, "_game"]),
        "move_num",
        1
    )
    move = Move()
    move.game_id = int(game_id)
    move.gamer_id = gamer_id
    move.x = x
    move.y = y
    move.num = num
    move.save()

    r.publish("".join(["thread_", game_id, "_game"]), json.dumps({
        "stat": "PROCESS",
        "x": str(x),
        "y": str(y),
        "uid": str(gamer_id),
    }))

    new_status = game.status
    if new_status == "WINNER":
        r.publish("".join(["thread_", game_id, "_game"]), json.dumps({
            "stat": new_status,
            "winner": game.winner,
        }))
    if new_status == "DRAW":
        r.publish("".join(["thread_", game_id, "_game"]), json.dumps({
            "stat": new_status,
        }))
