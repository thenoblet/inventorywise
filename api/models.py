"""
ApiKey model for managing API keys in the application.

This model handles the generation, storage, and management of API keys for
different applications and users. It includes features for hashing keys,
rate limiting, and tracking usage statistics.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import secrets
import hashlib

# Create your models here.


class ApiKey(models.Model):
    """
    Model representing an API key.
    """
    key = models.CharField(max_length=50, unique=True, editable=False)
    hashed_key = models.CharField(max_length=64)
    app_id = models.CharField(max_length=40, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rate_limit = models.IntegerField(default=100)  # requests per hour
    last_used = models.DateTimeField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        """
        Save the API key instance.

        If the instance is being created and does not have a key, a new
        API key is generated, and its hash is computed before saving
        to the database.

        Args:
            *args: Positional arguments passed to the parent save method.
            **kwargs: Keyword arguments passed to the parent save method.
        """
        if not self.pk and not self.key:
            self.key = self.generate_key()
            self.hashed_key = self.hash_key(
                self.key)  # Hash the key before saving

        super().save(*args, **kwargs)

    @property
    def is_expired(self):

        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at

    def increment_usage(self):
        """
        Increment the usage count of the API key and update the last
        used timestamp.

        This method should be called each time the API key is used to
        keep track of its usage and enforce rate limits.
        """
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save()

    @staticmethod
    def generate_key():
        """
        Generate a new API key.

        Returns:
            str: A securely generated API key.
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_key(key):
        """
        Hash the provided API key using SHA-256.

        Args:
            key (str): The API key to hash.

        Returns:
            str: The SHA-256 hash of the API key.
        """
        return hashlib.sha256(key.encode()).hexdigest()

    @classmethod
    def check_key(cls, key):
        """
        Check if the provided API key matches any stored keys.

        Args:
            key (str): The API key to check.

        Returns:
            ApiKey: The matching ApiKey instance, or None if not found.
        """
        hashed = cls.hash_key(key)
        return cls.objects.filter(hashed_key=hashed).first()

    def regenerate_key(self):
        """
        Mark the current API key as inactive and generate a new key.

        This method creates a new API key instance while preserving the
        existing application's ID and rate limit.

        Returns:
            str: The newly generated API key.
        """
        self.is_active = False
        self.save()

        # Create a new key instance
        new_key = ApiKey.objects.create(
            owner=self.owner,
            app_id=self.app_id,  # Use the same app_id
            rate_limit=self.rate_limit,  # Same rate limit as before
        )

        return new_key.key

    def __str__(self):
        """
        String representation of the ApiKey instance.

        Returns:
            str: A descriptive string representing the API key instance.
        """
        return f"API Key for {self.app_id} - Owned by {self.owner.username}"
