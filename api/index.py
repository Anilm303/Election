import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evoting.settings")

# Vercel Python runtime expects a WSGI app callable.
app = get_wsgi_application()
