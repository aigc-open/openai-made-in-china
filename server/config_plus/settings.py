from config.settings import *
INSTALLED_APPS.extend(["demo_api"])
ROOT_URLCONF = "config_plus.urls"
WSGI_APPLICATION = 'config_plus.wsgi.application'
