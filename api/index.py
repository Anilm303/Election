import os

import django
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evoting.settings")

if os.getenv("VERCEL") and not os.getenv("DATABASE_URL"):
	django.setup()
	call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)

# Vercel Python runtime expects a WSGI app callable.
app = get_wsgi_application()
