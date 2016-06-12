from django import forms
from tornado.models import *


class GameForm(forms.ModelForm):

    model = Game
    fields = ['name', 'sizeX', 'sizeY', 'participants', 'turn']


class MoveForm(forms.ModelForm):

    model = Move
    fields = ['x', 'y', 'game', 'gamer']
