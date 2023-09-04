from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('finances/', include('apps.finances.urls')),
    path('users/', include('apps.users.urls', namespace="users")),
]
