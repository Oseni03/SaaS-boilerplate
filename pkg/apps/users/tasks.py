from apps.users import tokens
from celery import shared_task
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string

from enums import EmailType

User = get_user_model()

@shared_task
def send_mail(type: str, user: str, **kwargs):
    user = User.objects.get(id=user)
    print(user.email)
    data={
        "domain": settings.DOMAIN,
        "site_name": settings.SITE_NAME,
        'user_id': user.id.hashid,
        **kwargs
    }
    if type == EmailType.ACCOUNT_CONFIRMATION.value:
        data["token"] = tokens.account_activation_token.make_token(user)
        subject = "Activate your Account"
        message = render_to_string(
            "users/emails/account_confirmation.html",
            data
        )
    elif type == EmailType.PASSWORD_RESET.value:
        data["token"] = tokens.password_reset_token.make_token(user)
        subject = "Reset your password"
        message = render_to_string(
            "users/emails/password_reset.html",
            data
        )
    elif type == EmailType.TRIAL_EXPIRES_SOON.value:
        subject = "Trial expires soon"
        message = render_to_string(
            "finances/emails/trial_expiring.html",
            data
        )
    elif type == EmailType.SUBSCRIPTION_ERROR.value:
        subject = "Subscription failure"
        message = render_to_string(
            "finances/emails/subscription_error.html",
            data
        )
    
    mail.send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    