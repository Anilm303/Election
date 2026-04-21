import os
import importlib

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evoting.settings")

import django
from django.core.management import call_command

django.setup()

# Always run migrations on Vercel
if os.getenv("VERCEL"):
	# Ensure migration files are part of the serverless bundle.
	try:
		importlib.import_module("voting.migrations.0001_initial")
		importlib.import_module("voting.migrations.0002_alter_customuser_managers_and_more")
		importlib.import_module("voting.migrations.0003_auditlog_captchalog_notificationlog_otpverification_and_more")
		importlib.import_module("voting.migrations.0004_alter_votelog_activity_type_alter_votelog_election")
	except ImportError:
		pass
	
	# Run migrations on connected database
	try:
		call_command("migrate", interactive=False, verbosity=0)
	except Exception as e:
		print(f"Migration warning: {e}")

from django.core.wsgi import get_wsgi_application

# Vercel Python runtime expects a WSGI app callable.
app = get_wsgi_application()
