from django.conf.urls import include, url

from django.contrib import admin
import tornado.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^tornado/', include('tornado.urls')),

    url(r'^$', tornado.views.home, name="home"),
]
