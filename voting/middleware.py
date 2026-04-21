import os
import threading

from django.core.management import call_command


_SCHEMA_BOOTSTRAPPED = False
_SCHEMA_BOOTSTRAP_LOCK = threading.Lock()


def _is_vercel_sqlite_fallback() -> bool:
    return os.getenv("VERCEL") and not (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL_NON_POOLING")
        or os.getenv("POSTGRES_URL")
        or os.getenv("POSTGRES_PRISMA_URL")
    )


def _ensure_schema_bootstrapped() -> None:
    global _SCHEMA_BOOTSTRAPPED
    if _SCHEMA_BOOTSTRAPPED:
        return
    with _SCHEMA_BOOTSTRAP_LOCK:
        if _SCHEMA_BOOTSTRAPPED:
            return
        call_command("migrate", interactive=False, verbosity=0, run_syncdb=True)
        _SCHEMA_BOOTSTRAPPED = True


class EnsureSchemaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if _is_vercel_sqlite_fallback():
            _ensure_schema_bootstrapped()
        return self.get_response(request)
