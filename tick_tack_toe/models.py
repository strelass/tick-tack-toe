from django.db import models
from django.db.models.signals import post_save

from django.contrib.auth.models import User


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
            return "Game %s was won by %s" % (self.id, self.winner.username)
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
        return "%s-%s:%s" % (self.num+1, self.x, self.y)


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


post_save.connect(update_last_message_datetime, sender=Message)
