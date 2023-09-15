from django.contrib import admin
from django.urls import path, include
from django.conf import settings

import debug_toolbar

urlpatterns = [
    path("", admin.site.urls),
    path("finances/", include("apps.finances.urls.admin")),
]

if settings.DEVELOPMENT_MODE is True:
    urlpatterns.append(
        path("__debug__", include(debug_toolbar.urls))
    )