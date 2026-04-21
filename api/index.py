import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evoting.settings")

import django
from django.core.management import call_command

django.setup()
call_command("migrate", interactive=False, verbosity=0)

from django.core.wsgi import get_wsgi_application

# Vercel Python runtime expects a WSGI app callable.
app = get_wsgi_application()
