import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evoting.settings")

import django

django.setup()

from django.core.wsgi import get_wsgi_application

# Vercel Python runtime expects a WSGI app callable.
app = get_wsgi_application()
