from rest_framework.permissions import BasePermission


class IsVerifiedUser(BasePermission):
    """
    Allows access only to authenticated and verified users.
    """

    message = "Your account must be verified to access this feature."

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_verified
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Anyone can read public data.

    Only staff/admin users can create,
    update or delete data.
    """

    def has_permission(self, request, view):

        # GET, HEAD and OPTIONS are public.
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        # Only staff users can modify data.
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )