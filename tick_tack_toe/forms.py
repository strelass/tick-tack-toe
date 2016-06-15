from django import forms
from tick_tack_toe.models import *


class GameForm(forms.ModelForm):

    class Meta:
        model = Game
        fields = ['name', 'first', 'sizeX', 'sizeY', 'combo', 'participants', 'turn']


class SimpleGameForm(forms.ModelForm):

    def clean_sizeX(self):
        data = self.cleaned_data['sizeX']
        if data < 3:
            raise forms.ValidationError("Size couldn't be less than %s." % 3)
        if data > 10:
            raise forms.ValidationError("Size couldn't be more than %s." % 10)
        return data

    def clean_sizeY(self):
        data = self.cleaned_data['sizeY']
        if data < 3:
            raise forms.ValidationError("Size couldn't be less than %s." % 3)
        if data > 10:
            raise forms.ValidationError("Size couldn't be more than %s." % 10)
        return data

    def clean(self):
        form_data = super(SimpleGameForm, self).clean()
        if self.errors:
            return form_data
        combo = form_data['combo']
        sizeX = form_data['sizeX']
        sizeY = form_data['sizeY']
        liniar_data = form_data['liniar_rool']
        diagonal_data = form_data['diagonal_rool']
        if combo < sizeX and combo < sizeY:
            self.add_error(
                'combo',
                'Combo cant be more that field size.',
            )
        if combo < 3:
            self.add_error(
                'combo',
                'Combo cant be less that 3.',
            )
        if not (liniar_data or diagonal_data):
            self.add_error(
                'liniar_rool',
                'You should choose one of the rools.',
            )
            self.add_error(
                'diagonal_rool',
                'You should choose one of the rools.',
            )
        return form_data

    class Meta:
        model = Game
        fields = ['name', 'sizeX', 'sizeY', 'combo', 'liniar_rool', 'diagonal_rool']


class MoveForm(forms.ModelForm):

    class Meta:
        model = Move
        fields = ['x', 'y', 'game', 'gamer']
