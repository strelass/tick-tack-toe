import json
from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User
import redis


class Thread(models.Model):
    participants = models.ManyToManyField(User)
    last_message = models.DateTimeField(null=True, blank=True, db_index=True)


class Message(models.Model):
    text = models.TextField()
    sender = models.ForeignKey(User)
    thread = models.ForeignKey(Thread)
    datetime = models.DateTimeField(auto_now_add=True, db_index=True)


class Game(models.Model):
    name = models.CharField(
        max_length=32,
        null=False,
        blank=True,
        default="Game",
    )
    sizeX = models.IntegerField(
        null=False,
        blank=True,
        default=3,
    )
    sizeY = models.IntegerField(
        null=False,
        blank=True,
        default=3,
    )
    participants = models.ManyToManyField(User)
    turn = models.ForeignKey(
        User,
        related_name="%(app_label)s_%(class)s_turn"
    )
    STATUS = (
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In progress"),
        ("DRAW", "Draw"),
        ("WINNER", "Winner"),
    )
    status = models.CharField(
        max_length=64,
        choices=STATUS,
        default="OPEN",
    )
    winner = models.ForeignKey(
        User,
        related_name="%(app_label)s_%(class)s_winner",
        null=True,
        blank=True,
    )

    def __unicode__(self):
        if self.status == "IN_PROGRESS":
            return "Game %s in progress" % self.id
        elif self.status == "DRAW":
            return "Game %s ends with draw" % self.id
        elif self.status == "WINNER":
            return "%s" % self.name
            # return "Game %s was won by %s" % (self.id, self.winner.username)
        else:
            return "Game %s is open" % self.id


class Move(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()
    num = models.IntegerField()
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )
    gamer = models.ForeignKey(User)

    def __unicode__(self):
        return "%s-%s:%s" % (self.num + 1, self.x, self.y)


def update_last_message_datetime(sender, instance, created, **kwargs):
    """
    Update Thread's last_message field when
    a new message is sent.
    """
    if not created:
        return

    Thread.objects.filter(id=instance.thread.id).update(
        last_message=instance.datetime
    )


def update_game(sender, instance, created, **kwargs):
    if not created:
        return
    game = instance.game
    moves = game.move_set.all()
    field = [[0 for i in xrange(game.sizeX)] for i in xrange(game.sizeY)]
    for move in moves:
        field[move.x][move.y] = move.gamer_id
    print field
    update_game_util(game, field, instance.x, instance.y)


def update_game_util(game, field, startX, startY):
    #     TODO: dynamically change game logic
    combo = 3
    linear_rools = [
        ((0, 1), (0, -1)),
        ((1, 0), (-1, 0)),
    ]
    diagonal_rools = [
        ((1, 1), (-1, -1)),
        ((-1, 1), (1, -1)),
    ]
    r = redis.StrictRedis()
    for i in linear_rools + diagonal_rools:
        count = 0
        for k in i:
            count += check_roole(field, startX, startY, k[0], k[1])
        if count + 1 == combo:
            game.status = "WINNER"
            game.winner = game.turn
            game.save()
            r.publish("".join(["thread_", str(game.id), "_game"]), json.dumps({
                "stat": game.status,
                "winner": game.winner.username,
            }))
            break
    if game.sizeX * game.sizeY == len(game.move_set.all()):
        game.status = "DRAW"
        game.save()
        r.publish("".join(["thread_", str(game.id), "_game"]), json.dumps({
            "stat": game.status,
        }))
    if game.status == "IN_PROGRESS":
        game.turn = game.participants.exclude(id=game.turn.id).first()


def check_roole(matrix, startX, startY, rooleX, rooleY):
    combo = 0
    x = startX
    y = startY
    gamer = matrix[x][y]
    while 0 <= x < len(matrix) and 0 <= y < len(matrix[0]) and matrix[x][y] == gamer:
        x, y, combo = x + rooleX, y + rooleY, combo + 1
    return combo - 1


post_save.connect(update_game, sender=Move)
post_save.connect(update_last_message_datetime, sender=Message)
