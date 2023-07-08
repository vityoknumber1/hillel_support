from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from tickets.models import Ticket
from users.constants import Role
from users.models import User


class RoleIsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == Role.ADMIN


class RoleIsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == Role.MANAGER


class RoleIsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == Role.USER


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj: Ticket):
        return obj.user == request.user


class UserIsNewManager(BasePermission):
    def has_permission(self, request, view):
        new_manager_id = request.data["new_manager"]
        ticket_id = request.parser_context["kwargs"]["pk"]

        try:
            ticket = Ticket.objects.get(id=ticket_id)
            user = User.objects.get(id=new_manager_id)
        except Ticket.DoesNotExist:
            raise PermissionDenied(
                f"Ticket with ID {ticket_id} \
                                   does not exist."
            )
        except User.DoesNotExist:
            raise PermissionDenied(
                f"User with ID {new_manager_id} \
                                   does not exist."
            )

        if user.role != Role.MANAGER:
            raise PermissionDenied(
                f"User with ID {new_manager_id} \
                                   is not a manager."
            )

        if ticket.manager_id == new_manager_id:
            raise PermissionDenied(
                "Cannot assign current manager \
                                   as the new manager."
            )

        return True
