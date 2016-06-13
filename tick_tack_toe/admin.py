from django.contrib import admin
from tick_tack_toe.forms import GameForm, MoveForm
from tick_tack_toe.models import Game, Move


class GameAdmin(admin.ModelAdmin):
    form = GameForm
    list_display = [
        'id',
        'name',
        'sizeX',
        'sizeY',
        'combo',
        'status',
        'winner',
    ]
    readonly_fields = ('winner',)
    search_fields = ('name',)
    ordering = ('-id',)
    filter_horizontal = ()


class MoveAdmin(admin.ModelAdmin):
    form = MoveForm
    list_display = [
        'x', 'y', 'game', 'gamer'
    ]


admin.site.register(Game, GameAdmin)
admin.site.register(Move, MoveAdmin)
