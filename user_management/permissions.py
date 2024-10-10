"""
Module: permissions

This module provides utilities for checking user permissions based on their roles.
It assumes a relationship between users, roles, and permissions where each user
is assigned one or more roles, and each role has a set of permissions.

Models used:
- `UserRole`: A model linking users to their roles.
- `RolePermission`: A model linking roles to their associated permissions.
"""

from .models import UserRole, RolePermission

def has_permission(user, permission):
    user_roles = UserRole.objects.filter(user=user).values_list('role', flat=True)
    
    role_permissions = RolePermission.objects.filter(role__in=user_roles).values_list('permission__name', flat=True)
    
    return permission in role_permissions
