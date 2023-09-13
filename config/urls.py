from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('finances/', include('apps.finances.urls', namespace="finances")),
    path('users/', include('apps.users.urls', namespace="users")),
    path('notifications/', include('apps.notifications.urls', namespace="notifications")),
    path('accounts/', include('allauth.urls')),
]
