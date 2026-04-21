import os

from django.core.management import call_command
from django.db import OperationalError


class EnsureSchemaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        using_vercel_fallback = os.getenv("VERCEL") and not (
            os.getenv("DATABASE_URL")
            or os.getenv("POSTGRES_URL_NON_POOLING")
            or os.getenv("POSTGRES_URL")
            or os.getenv("POSTGRES_PRISMA_URL")
        )

        if not using_vercel_fallback:
            return self.get_response(request)

        try:
            return self.get_response(request)
        except OperationalError as exc:
            if getattr(request, "_schema_retry_done", False):
                raise
            if "no such table" not in str(exc).lower():
                raise

            request._schema_retry_done = True
            call_command("migrate", interactive=False, verbosity=0, run_syncdb=True)
            return self.get_response(request)
