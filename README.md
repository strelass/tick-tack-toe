# Tornado WebSocket tick-tack-toe game for Django

To run this app you will need:
* [Python 2.7](https://www.python.org/download/releases/2.7/)
* [Redis](http://redis.io/). If it has specific setting you should set it in setting.py file.
* Any SQL database you want, but don't forget to set its parameters in setting.py. Right here i'm using MySQL.
After you got this go to the root of project and run following commands:
1. <b>pip install requirments.txt</b>
2. <b>python manage.py migrate</b>
3. <b>python mamage.py collectstatic</b>
4. <b>python manage.py runserver</b>
Now you will need another bash window, where you can run:
  <b>python manage.py starttornadoapp</b> Make sure that you have 8888 port free.

Enjoy!
