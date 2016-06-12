from django.conf.urls import url
from tornado import views

urlpatterns = [
    url(r'^send_message/$', views.send_message_view, name="send_message"),
    url(r'^send_message_api/(?P<thread_id>\d+)/$', views.send_message_api_view, name="send_message_api"),
    url(r'^chat/(?P<thread_id>\d+)/$', views.chat_view, name="chat"),
    url(r'^$', views.messages_view, name="messages"),
    url(r'^lobby/$', views.lobby, name="lobby"),
    url(r'^game/(?P<game_id>\d+)/$', views.game_view, name="game"),
    url(r'^make_move_api/(?P<game_id>\d+)/$', views.make_move_view_api, name="make_move_api"),
]
