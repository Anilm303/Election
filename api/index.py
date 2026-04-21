import os
import importlib

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
	# Ensure migration files are part of the serverless bundle.
	importlib.import_module("voting.migrations.0001_initial")
	importlib.import_module("voting.migrations.0002_alter_customuser_managers_and_more")
	importlib.import_module("voting.migrations.0003_auditlog_captchalog_notificationlog_otpverification_and_more")
	importlib.import_module("voting.migrations.0004_alter_votelog_activity_type_alter_votelog_election")
	call_command("migrate", interactive=False, verbosity=0, run_syncdb=True)

from django.core.wsgi import get_wsgi_application

# Vercel Python runtime expects a WSGI app callable.
app = get_wsgi_application()
