import os
import threading

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import OperationalError


_SCHEMA_BOOTSTRAPPED = False
_SCHEMA_BOOTSTRAP_LOCK = threading.Lock()


def _is_vercel_sqlite_fallback() -> bool:
    return os.getenv("VERCEL") and not (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL_NON_POOLING")
        or os.getenv("POSTGRES_URL")
        or os.getenv("POSTGRES_PRISMA_URL")
    )


def _is_schema_missing() -> bool:
    if not os.getenv("VERCEL"):
        return False

    try:
        from django.db import connection

        with connection.cursor() as cursor:
            tables = connection.introspection.table_names(cursor)
        return "auth_user" not in tables
    except Exception:
        return True


def _ensure_schema_bootstrapped() -> None:
    global _SCHEMA_BOOTSTRAPPED
    if _SCHEMA_BOOTSTRAPPED:
        return
    with _SCHEMA_BOOTSTRAP_LOCK:
        if _SCHEMA_BOOTSTRAPPED:
            return
        call_command("migrate", interactive=False, verbosity=0, run_syncdb=True)
        _SCHEMA_BOOTSTRAPPED = True


def _ensure_superuser_from_env() -> bool:
    username = (os.getenv("DJANGO_SUPERUSER_USERNAME") or "").strip()
    email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or "").strip()
    password = (os.getenv("DJANGO_SUPERUSER_PASSWORD") or "").strip()
    if not username or not email or not password:
        return False

    user_model = get_user_model()
    user, created = user_model.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
        },
    )

    changed = created
    if user.email != email:
        user.email = email
        changed = True
    if not user.is_staff:
        user.is_staff = True
        changed = True
    if not user.is_superuser:
        user.is_superuser = True
        changed = True
    if not user.is_active:
        user.is_active = True
        changed = True
    if not user.check_password(password):
        user.set_password(password)
        changed = True

    if changed:
        user.save()
    return True


class EnsureSchemaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if _is_vercel_sqlite_fallback() or _is_schema_missing():
            _ensure_schema_bootstrapped()
        return self.get_response(request)
