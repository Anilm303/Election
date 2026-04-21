from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.templatetags.static import static as static_tag
from django.urls import include, path
from django.views.generic import RedirectView


urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url=static_tag("voting/favicon.svg"), permanent=False)),
    path("admin/", admin.site.urls),
    path("rosetta/", include("rosetta.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("", include("voting.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
