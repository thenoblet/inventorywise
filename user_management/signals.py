"""
Signals module for user management in Django.

This module contains signal receivers that handle actions related to the
User model.
It listens for the `post_save` signal from the User model to automatically
create or update associated Profile objects.

Signal receivers:
- create_profile: Creates a Profile instance whenever a new User is created.
- save_profile: Saves the Profile instance whenever the associated User
  is saved.

This helps maintain consistency between User and Profile objects within the
application.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a Profile object whenever a new
    User is created.

    This function is triggered after a User instance is saved to the database.
    If the User instance is being created for the first time
    (`created` is True), a corresponding Profile object is automatically
    created and linked to the User.

    Args:
        sender (class): The model class (User) sending the signal.
        instance (User): The instance of the User model being saved.
        created (bool): A boolean indicating whether the User was
                        created (True) or updated (False).
        **kwargs: Additional keyword arguments.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Signal receiver that saves the Profile object whenever the associated
    User is saved.

    This function ensures that any changes to the User instance are also
    saved to the related Profile instance by calling `save()` on the Profile.

    Args:
        sender (class): The model class (User) sending the signal.
        instance (User): The instance of the User model being saved.
        **kwargs: Additional keyword arguments.
    """
    instance.profile.save()
