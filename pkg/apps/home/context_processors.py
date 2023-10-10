from django.conf import settings


def home(request):
    return {"site_name": settings.SITE_NAME}