from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission class that allows only the owner of a task to edit it.

    This permission grants read-only access to any request method classified as 'SAFE'
    (GET, HEAD, OPTIONS) to any user, but restricts write permissions (POST, PUT, PATCH, DELETE)
    to the owner of the task only.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check if the request should be permitted.

        Args:
            request: HttpRequest object.
            view: The view which is being accessed.
            obj: The object being accessed - in this case, a Task instance.

        Returns:
            bool: True if the request is permitted, False otherwise.
        """
        # Allow read-only access for safe methods for any user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the task
        return obj.owner == request.user
