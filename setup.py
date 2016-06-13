#!/usr/bin/env python

from setuptools import setup

setup(
    # GETTING-STARTED: set your app name:
    name='evo',
    # GETTING-STARTED: set your app version:
    version='1.0',
    # GETTING-STARTED: set your app description:
    description='OpenShift App',
    # GETTING-STARTED: set author name (your name):
    author='Arrow',
    # GETTING-STARTED: set author email (your email):
    author_email='knu.timetable@gmail.com',
    # GETTING-STARTED: set author url (your url):
    url='http://www.python.org/sigs/distutils-sig/',
    # GETTING-STARTED: define required django version:
    install_requires=[
        'dj-static==0.0.6',
        'Django==1.9.5',
        'django-allauth==0.25.2',
        'django-crispy-forms==1.6.0',
        'django-jquery-js==2.1.4',
        'django-registration-redux==1.4',
        'google-api-python-client==1.4.2',
        'httplib2==0.9.2',
        'mysql-connector-python==2.0.4',
        'MySQL-python==1.2.5',
        'oauth2client==1.5.2',
        'oauthlib==1.0.3',
        'Pillow==3.1.1',
        'python-openid==2.2.5',
        'requests==2.9.1',
        'requests-oauthlib==0.6.1',
        'django-redis-sessions==0.5.6',
        'TornadIO2==0.0.4',
        'django-websocket-redis==0.4.6',
        'redis==2.10.5',
        'tornado==4.3,'
        'tornado-redis==2.4.18',
        'sockjs-tornado==1.0.3',
    ],
)