import json
import re
import redis

from django.contrib.auth.models import User
from django.http import HttpResponse
from tick_tack_toe.models import Move, Game


r = redis.StrictRedis()

linear_rools = [
        ((0, 1), (0, -1)),
        ((1, 0), (-1, 0)),
    ]
diagonal_rools = [
    ((1, 1), (-1, -1)),
    ((-1, 1), (1, -1)),
]


def json_response(obj):
    return HttpResponse(
        json.dumps(obj),
        content_type='application/json',
    )


def redis_publish_game(game_id, context):
    r.publish("".join(["thread_", str(game_id), "_game"]), json.dumps(context))


def redis_set_game(game_id, field, value):
    game_id = str(game_id)
    r.hset(
        "".join(["thread_", game_id, "_game"]),
        str(field),
        str(value)
    )


def join_game(game_id, gamer_id, username):
    game_id = str(game_id)
    redis_publish_game(game_id, {
        "stat": "JOIN",
        "gamer_id": str(gamer_id),
        "gamer_name": username,
    })
    publish_game_status(Game.objects.get(id=game_id))


def start_game(game_id, turn):
    game_id = str(game_id)
    redis_publish_game(game_id, {
        "stat": "START",
        "turn": str(turn),
    })


def try_to_make_move(game, move, gamer):
    if gamer not in game.participants.all():
        return {"error": "Dont do this!."}
    print "TRY_TO_MAKE_MOVE: %s - %s - %s" % (gamer, game.turn, gamer == game.turn)
    if gamer != game.turn:
        return {"error": "Its not your turn."}
    if not re.match("^\d+:\d+$", move):
        return {"error": "Wrong move format."}

    x = int(move.split(":")[0])
    y = int(move.split(":")[1])
    if not (0 <= x < game.sizeX and 0 <= y < game.sizeY):
        return {"error": "Wrong move format."}

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
    game_id = str(game_id)
    print "MAKE_MOVE: %s:%s" % (x, y)
    move = Move()
    move.game_id = int(game_id)
    move.gamer_id = gamer_id
    move.x = x
    move.y = y
    move.save()
    update_game(game_id, x, y)

    redis_publish_game(game_id, {
        "stat": "PROCESS",
        "x": str(x),
        "y": str(y),
        "uid": str(gamer_id),
    })


def update_game(game_id, x, y):
    game = Game.objects.get(id=int(game_id))
    moves = game.move_set.all()
    field = [[0 for i in xrange(game.sizeY)] for i in xrange(game.sizeX)]
    for move in moves:
        field[move.x][move.y] = move.gamer_id
    print field
    update_game_util(game, field, x, y)


def update_game_util(game, field, startX, startY):
    #     TODO: dynamically change game logic
    old_status = game.status
    if game.status == "START":
        game.status = "IN_PROGRESS"
        game.save()
    combo = game.combo
    rools = []
    if game.liniar_rool:
        rools += linear_rools
    if game.diagonal_rool:
        rools += diagonal_rools
    for i in rools:
        count = 0
        for k in i:
            count += check_roole(field, startX, startY, k[0], k[1])
        if count + 1 == combo:
            game.status = "WINNER"
            game.winner = User.objects.get(id=field[startX][startY])
            game.save()
            break
    if game.sizeX * game.sizeY == len(game.move_set.all()) and game.status != "WINNER":
        game.status = "DRAW"
        game.save()
    if game.status == "IN_PROGRESS":
        game.turn = game.participants.exclude(id=game.turn.id).first()
        game.save()
        print "Now is %s turn" % game.turn
    if game.status != old_status:
        publish_game_status(game)


def publish_game_status(game):
    winner = str(game.winner.id) if (game.status == "WINNER") else ""
    print "%s" % game.first
    redis_publish_game(game.id, {
        "stat": "GAME_STATUS",
        "game_status": game.status,
        "turn": str(game.turn.id),
        "first_turn": str(game.first.id),
        "winner": winner,
    })


def check_roole(matrix, startX, startY, rooleX, rooleY):
    combo = 0
    x = startX
    y = startY
    gamer = matrix[x][y]
    while 0 <= x < len(matrix) and 0 <= y < len(matrix[0]) and matrix[x][y] == gamer:
        x, y, combo = x + rooleX, y + rooleY, combo + 1
    return combo - 1
