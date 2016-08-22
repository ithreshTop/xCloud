"""
WSGI config for xcloud project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
import sys
import site

ROOT_DIR = '/var/www/html/xcloud/xcloud'
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

 

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xcloud.settings")
os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs'
 
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
