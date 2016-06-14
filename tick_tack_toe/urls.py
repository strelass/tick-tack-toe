from django.conf.urls import url
from tick_tack_toe import views

urlpatterns = [
    url(r'^lobby/$', views.lobby, name="lobby"),
    url(r'^game/(?P<game_id>\d+)/$', views.game_view, name="game"),
    url(r'^make_move_api/(?P<game_id>\d+)/$', views.make_move_view_api, name="make_move_api"),
]
