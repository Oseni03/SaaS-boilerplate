from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=models.User)
def create_user_profile(sender, instance: models.User, created, update_fields, **kwargs):
    if created:
        models.UserProfile.objects.create(user=instance)
        