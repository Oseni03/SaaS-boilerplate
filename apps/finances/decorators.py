from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings
 
 
def subscription_test(user):
    if user.is_subscribed or not settings.SUBSCRIPTION_ENABLE:
        return True
    return False


def subscribe_required(redirect_url="finances:pricing"):
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            if not subscription_test(request.user):
                return redirect(redirect_url)
            return view(request, *args, **kwargs)
        return _wrapped_view
    return decorator