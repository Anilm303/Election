import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evoting.settings")

import django
from django.core.management import call_command

django.setup()

# If no external database is configured on Vercel, initialize fallback SQLite schema.
if os.getenv("VERCEL") and not (
	os.getenv("DATABASE_URL")
	or os.getenv("POSTGRES_URL_NON_POOLING")
	or os.getenv("POSTGRES_URL")
	or os.getenv("POSTGRES_PRISMA_URL")
):
	call_command("migrate", interactive=False, verbosity=0)

from django.core.wsgi import get_wsgi_application

# Vercel Python runtime expects a WSGI app callable.
app = get_wsgi_application()
