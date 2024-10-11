"""
Module: user_management

This module defines custom user models, roles, permissions, and profile models
for managing users, their roles, permissions, and related functionality.
It uses Django's built-in authentication system and extends it with
additional features such as role-based permissions.
"""

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin)
from django.db import models
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


# Create your models here.
class CustomUserManager(BaseUserManager):
    """
    Custom manager for handling user creation and modification.

    Methods:
        - create_user: Creates a new regular user.
        - create_superuser: Creates a new superuser with elevated permissions.
        - remove_user: Deactivates a user based on their email.
        - update_user: Updates user information by email.
    """

    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and save a regular user with the given email, username,
        and password.
        """
        if not email:
            raise ValueError("The email field is required")

        if password is None:
            raise ValueError("The password field is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and save a superuser with elevated permissions.
        """
        if not email:
            raise ValueError("The email field is required")

        if password is None:
            raise ValueError("The password field is required")

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

    def remove_user(self, email):
        """
        Deactivate a user by setting their 'is_active' field to False.

        If no user is found, it raises a `User.DoesNotExist` exception.
        """
        try:
            user = self.get(email=email)
            user.is_active = False
            user.save(using=self._db, update_fields=['is_active'])
        except self.model.DoesNotExist:
            raise ValueError(f"User with email: {email} does not exist")

    def update_user(self, email, **update_fields):
        """
        Update a user's information based on their email.
        The `updated_fields` argument contains the fields to update.
        If the user is not found, it raises a `User.DoesNotExist` exception.
        """
        try:
            user = self.get(email=email)
            for field, value in update_fields.items():
                setattr(user, field, value)
            user.save(using=self._db)
        except self.model.DoesNotExist:
            raise ValueError(f"User with email: {email} does not exist")


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    password = models.CharField(max_length=128)
    firstname = models.CharField(max_length=255)
    middlename = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'firstname', 'lastname']

    class Meta:
        db_table = "user"

    def __str__(self):
        return self.email

    def to_dict(self):
        """
        Return a dictionary representation of the user object.
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'firstname': self.firstname,
            'middlename': self.middlename,
            'lastname': self.lastname,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def clean(self):
        """
        Validate the password using Django's built-in password validation
        system.
        Raises a ValidationError if the password is invalid.
        """
        super().clean()
        try:
            validate_password(self.password)
        except ValidationError as e:
            raise ValidationError({'password': e.messages})


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to='profile/avatars', blank=True, null=True)

    class Meta:
        db_table = "profile"

    def __str__(self):
        return f"{self.user.username} Profile"


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "role"
    
    def add_permission(self, permission_name):
        perm, _ = Permission.objects.get_or_create(name=permission_name)
        RolePermission.objects.get_or_create(role=self, permission=perm)
    
    def remove_permission(self, permission_name):
        RolePermission.objects.filter(role=self, permission__name=permission_name).delete()
        
    def get_permissions(self):
        return [rp.permission.name for rp in self.rolepermission_set.all()]

    def __str__(self):
        return self.name


class Permission(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "permissions"

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_index=True)

    class Meta:
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_index=True)
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, db_index=True)

    class Meta:
        unique_together = ('role', 'permission')

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"

