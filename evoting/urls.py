from django.contrib import admin
from django.templatetags.static import static
from django.urls import include, path
from django.views.generic import RedirectView


urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url=static("voting/favicon.svg"), permanent=False)),
    path("admin/", admin.site.urls),
    path("", include("voting.urls")),
]
