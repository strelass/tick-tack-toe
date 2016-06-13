import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ON_OPENSHIFT = False
if 'OPENSHIFT_REPO_DIR' in os.environ:
    ON_OPENSHIFT = True

DEFAULT_CHARSET = 'utf-8'

SECRET_KEY = '=b_8$k&wjhoz#&fk2yk&9xpxo@i1+!(=g4_1!-j-pk%er&u*0s'

ALLOWED_HOSTS = []

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'knu.timetable@gmail.com'
EMAIL_HOST_PASSWORD = 'knu_IS-4_2016'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ADMINS = (
    # ('Vlad Strelnikov', 'vlad.sstrelnikov@gmail.com'),
)

MANAGERS = ADMINS

DEBUG = True

LIB_APPS = [
    'crispy_forms',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]
MY_APPS = [
    'tick_tack_toe',
]
DJANGO_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
]

INSTALLED_APPS = DJANGO_APPS + MY_APPS + LIB_APPS

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'myproject.urls'

WSGI_APPLICATION = 'myproject.wsgi.application'

if ON_OPENSHIFT:
    DEBUG = False
    ALLOWED_HOSTS = ['*']
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'python',
            'USER': os.getenv('OPENSHIFT_MYSQL_DB_USERNAME'),
            'PASSWORD': os.getenv('OPENSHIFT_MYSQL_DB_PASSWORD'),
            'HOST': os.getenv('OPENSHIFT_MYSQL_DB_HOST'),
            'PORT': os.getenv('OPENSHIFT_MYSQL_DB_PORT'),
            }
    }
else:
    DEBUG = True
    ALLOWED_HOSTS = []
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'tick_tack_toe',
            'USER': 'root',
            'PASSWORD': 'root',
        }
    }

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

SITE_ID = 1
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = True
LOGIN_REDIRECT_URL = '/'

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
if ON_OPENSHIFT:
    STATIC_ROOT = os.path.join(BASE_DIR, 'wsgi', "static")
    MEDIA_ROOT = os.path.join(os.environ.get('OPENSHIFT_DATA_DIR', ''), 'media')
else:
    STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static", "static_root")
    MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static", "media_root")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static", "mystatic"),
)

CRISPY_TEMPLATE_PACK = 'bootstrap4'
CRISPY_FAIL_SILENTLY = not DEBUG

LOGIN_URL = '/user/'

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

#-----DEBUG-----
SESSION_ENGINE = 'redis_sessions.session'

API_KEY = '$0m3-U/\/1qu3-K3Y'

SEND_MESSAGE_API_URL = 'http://127.0.0.1:8000/tick_tack_toe/send_message_api'
MAKE_MOVE_API_URL = 'http://127.0.0.1:8000/tick_tack_toe/make_move_api'
