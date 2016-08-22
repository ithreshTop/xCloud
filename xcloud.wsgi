#!/usr/bin/env python
import os
import sys
import site

ROOT_DIR = '/usr/local/xcloud/'
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xcloud.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
