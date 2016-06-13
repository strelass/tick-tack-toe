from django import forms
from tick_tack_toe.models import *


class GameForm(forms.ModelForm):

    class Meta:
        model = Game
        fields = ['name', 'sizeX', 'sizeY', 'combo', 'participants', 'turn']


class SimpleGameForm(forms.ModelForm):

    class Meta:
        model = Game
        fields = ['name', 'sizeX', 'sizeY', 'combo']


class MoveForm(forms.ModelForm):

    class Meta:
        model = Move
        fields = ['x', 'y', 'game', 'gamer']