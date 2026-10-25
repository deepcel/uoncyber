from rest_framework.exceptions import PermissionDenied

from accounts.permissions import is_admin


def is_module_owner(user):
    return is_admin(user) or (user.is_authenticated and user.role == 'OWNER')


def check_can_author(user):
    if not is_module_owner(user):
        raise PermissionDenied('Module owner access required.')


def check_module_owner(user, module):
    check_can_author(user)

    if not is_admin(user) and module.created_by_id != user.id:
        raise PermissionDenied('You do not manage this module.')


def check_pathway_owner(user, pathway):
    check_can_author(user)

    if not is_admin(user) and pathway.owner_id != user.id:
        raise PermissionDenied('You do not manage this pathway.')
