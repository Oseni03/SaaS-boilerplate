from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .services import subscriptions

User = get_user_model()


@receiver(post_save, sender=User)
def create_free_plan_subscription(sender, instance, created, **kwargs):
    if created:
        if settings.ENABLE_SUBSCRIPTION and settings.HAS_TRIAL_PERIOD_OR_FREE:
            subscriptions.initialize_user(user=instance)
