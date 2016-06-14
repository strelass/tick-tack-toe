from django.conf.urls import include, url

from django.contrib import admin
import tick_tack_toe.views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^tick_tack_toe/', include('tick_tack_toe.urls')),

    url(r'^$', tick_tack_toe.views.home, name="home"),
]
