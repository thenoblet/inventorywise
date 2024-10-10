"""
Admin module for managing user-related models.

This module registers the following models to the Django admin interface:
- User: Represents a system user.
- Role: Represents different roles that a user can have.
- Permission: Defines permissions that can be assigned to roles.
- UserRole: Manages the many-to-many relationship between users and roles.
- RolePermission: Manages the many-to-many relationship between roles and permissions.

By registering these models, admins can create, view, update, and delete instances
of these models via the admin interface.
"""

from django.contrib import admin
from .models import User, Role, Permission, UserRole, RolePermission


# Register your models here.
admin.site.register(User)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(UserRole)
admin.site.register(RolePermission)