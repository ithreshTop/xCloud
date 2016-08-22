from __future__ import absolute_import
import os
from celery import Celery,platforms
from xcloud import local_settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xcloud.settings')
from django.conf import settings  # noqa


app = Celery('xcloud',
             broker=settings.BROKER_URL)
platforms.C_FORCE_ROOT = True
app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)


app.config_from_object('django.conf:settings')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


