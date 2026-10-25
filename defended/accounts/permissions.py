from rest_framework.permissions import BasePermission


# Superusers count as admins so a `createsuperuser` account is never locked out.
def is_admin(user):
    return user.is_authenticated and (user.role == 'ADMIN' or user.is_superuser)


class IsAdminRole(BasePermission):

    message = 'Admin access required.'

    def has_permission(self, request, view):
        return is_admin(request.user)
