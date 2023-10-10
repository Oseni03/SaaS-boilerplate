from celery import shared_task
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string


@shared_task
def contact_us_email(name: str, email: str, message: str):
    data={
        "domain": settings.DOMAIN,
        "site_name": settings.SITE_NAME,
        "name": name,
        "email": email,
        "message": message,
    }
    
    subject = f"{settings.SITE_NAME} - Contact message"
    message = render_to_string(
        "home/emails/contact_us.html",
        data
    )
    mail.send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, settings.ADMINS)