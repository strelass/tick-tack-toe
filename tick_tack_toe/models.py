import json
from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User
import redis


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
    combo = models.IntegerField(
        null=False,
        blank=True,
        default=3,
    )
    liniar_rool = models.BooleanField(
        blank=True,
        default=True,
        verbose_name="Liniar rool",
    )
    diagonal_rool = models.BooleanField(
        blank=True,
        default=True,
        verbose_name="Diagonal rool",
    )
    participants = models.ManyToManyField(User)
    turn = models.ForeignKey(
        User,
        related_name="%(app_label)s_%(class)s_turn"
    )
    STATUS = (
        ("OPEN", "Open"),
        ("START", "Start"),
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
        return "%s:%s" % (self.id, self.name)


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
        return "%s - %s:%s" % (self.gamer.username, self.x, self.y)


def update_game(sender, instance, created, **kwargs):
    if not created:
        return
    game = instance.game
    moves = game.move_set.all()
    field = [[0 for i in xrange(game.sizeY)] for i in xrange(game.sizeX)]
    for move in moves:
        field[move.x][move.y] = move.gamer_id
    print field
    update_game_util(game, field, instance.x, instance.y)


linear_rools = [
        ((0, 1), (0, -1)),
        ((1, 0), (-1, 0)),
    ]
diagonal_rools = [
    ((1, 1), (-1, -1)),
    ((-1, 1), (1, -1)),
]


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
    r = redis.StrictRedis()
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
        r.publish(
            "".join(["thread_", str(game.id), "_game"]), json.dumps({
                "stat": "GAME_STATUS",
                "game_status": game.status,
                "winner": str(game.winner.id) if (game.status == "WINNER") else "",
            }))


def check_roole(matrix, startX, startY, rooleX, rooleY):
    combo = 0
    x = startX
    y = startY
    gamer = matrix[x][y]
    while 0 <= x < len(matrix) and 0 <= y < len(matrix[0]) and matrix[x][y] == gamer:
        x, y, combo = x + rooleX, y + rooleY, combo + 1
    return combo - 1


post_save.connect(update_game, sender=Move)
