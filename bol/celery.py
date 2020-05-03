from __future__ import absolute_import
import os
import django

from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bol.settings')
django.setup()


app = Celery('bol', backend='redis://localhost', borker='redis://localhost:6379/0')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(settings.INSTALLED_APPS)