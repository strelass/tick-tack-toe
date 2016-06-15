from django.db import models

from django.contrib.auth.models import User


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
    first = models.ForeignKey(
        User,
        related_name="%(app_label)s_%(class)s_first"
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
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE
    )
    gamer = models.ForeignKey(User)

    def __unicode__(self):
        return "%s - %s:%s" % (self.gamer.username, self.x, self.y)
