import os
import importlib

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evoting.settings")

import django
from django.core.management import call_command
from django.db import connection

django.setup()

# Ensure missing columns exist (fallback if migrations don't run)
def ensure_schema():
	"""Ensure critical database schema exists"""
	from django.conf import settings
	
	try:
		db_engine = settings.DATABASES['default']['ENGINE']
		is_sqlite = 'sqlite' in db_engine
		is_postgres = 'psycopg' in db_engine or 'postgresql' in db_engine
		
		with connection.cursor() as cursor:
			column_exists = False
			
			if is_sqlite:
				# For SQLite: use PRAGMA
				cursor.execute("PRAGMA table_info(voting_election)")
				columns = cursor.fetchall()
				column_exists = any(col[1] == 'allow_voting' for col in columns)
			elif is_postgres:
				# For PostgreSQL: use information_schema
				cursor.execute("""
					SELECT EXISTS (
						SELECT 1 FROM information_schema.columns 
						WHERE table_name = 'voting_election' 
						AND column_name = 'allow_voting'
					)
				""")
				column_exists = cursor.fetchone()[0]
			
			if not column_exists:
				try:
					cursor.execute("ALTER TABLE voting_election ADD COLUMN allow_voting boolean DEFAULT true;")
					print("[SCHEMA] Added allow_voting column to voting_election table")
				except Exception as e:
					print(f"[SCHEMA] Could not add column: {e}")
	except Exception as e:
		print(f"[SCHEMA] Check failed: {e}")

# Always run migrations on Vercel
if os.getenv("VERCEL"):
	# Ensure migration files are part of the serverless bundle.
	try:
		importlib.import_module("voting.migrations.0001_initial")
		importlib.import_module("voting.migrations.0002_alter_customuser_managers_and_more")
		importlib.import_module("voting.migrations.0003_auditlog_captchalog_notificationlog_otpverification_and_more")
		importlib.import_module("voting.migrations.0004_alter_votelog_activity_type_alter_votelog_election")
	except ImportError as e:
		print(f"Import error: {e}")
	
	# Run migrations on connected database
	try:
		print("[MIGRATION] Running Django migrations...")
		call_command("migrate", interactive=False, verbosity=2)
		print("[MIGRATION] Migrations completed successfully")
	except Exception as e:
		print(f"[MIGRATION ERROR] {e}")
		import traceback
		traceback.print_exc()

from django.core.wsgi import get_wsgi_application

# Vercel Python runtime expects a WSGI app callable.
app = get_wsgi_application()
