import os
import boto3
import json
from datetime import datetime

from django.conf import settings
from django.template.loader import render_to_string


client = boto3.client('ses')


def send_email(event, context):
    detail_type = event.get("DetailType")
    source = event.get("Source")
    event_bus = event.get("EventBusName")
    detail = event.get("Detail")
    
    to = detail.get("to")
    if detail_type == "CUSTOM_MAIL":
        body_html = render_to_string(
            "emails/custom_mail.html",
            detail
        )
        subject = detail.get("subject")
    elif detail_type == "SUBSCRIPTION_ERROR":
        body_html = render_to_string(
            "emails/subscription_error.html",
            detail
        )
        subject = ""
    elif detail_type == "ACCOUNT_ACTIVATION":
        body_html = render_to_string(
            "emails/account_activation.html",
            detail
        )
        subject = ""
    elif detail_type == "PASSWORD_RESET":
        body_html = render_to_string(
            "emails/password_reset.html",
            detail
        )
        subject = ""
    elif detail_type == "TRIAL_EXPIRES_SOON":
        body_html = render_to_string(
            "emails/trial_expiring.html",
            detail
        )
        subject = ""
    
    email_message = {
        'Body': {
            'Html': {
                'Charset': 'utf-8',
                'Data': body_html,
            },
        },
        'Subject': {
            'Charset': 'utf-8',
            'Data': subject,
        },
    }

    client.send_email(
        Destination={
            'ToAddresses': [to],
        },
        Message=email_message,
        Source=settings.DEFAULT_FROM_EMAIL,
    )