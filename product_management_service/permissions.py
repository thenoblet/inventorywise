from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins to edit an object.
    Read-only access is available to all users.
    """

    def has_permission(self, request, view):
        # Allow read-only access for GET, HEAD, OPTIONS requests
        if request.method in SAFE_METHODS:
            return True
        # Write permissions are only allowed for admin users
        return request.user and request.user.is_staff
