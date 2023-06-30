from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from tickets.models import Message, Ticket
from tickets.permissions import IsOwner, RoleIsAdmin, RoleIsManager, RoleIsUser
from tickets.serializers import TicketAssignSerializer, TicketSerializer
from users.constants import Role
from users.models import User


class TicketAPIViewSet(ModelViewSet):
    serializer_class = TicketSerializer

    def get_queryset(self):
        user = self.request.user
        all_tickets = Ticket.objects.all()

        match user.role:
            case Role.ADMIN:
                return all_tickets
            case Role.MANAGER:
                return all_tickets.filter(Q(manager=user) | Q(manager=None))
            case Role.USER:
                return all_tickets.filter(user=user)

    def get_permissions(self):
        match self.action:
            case "list":
                permission_classes = [RoleIsAdmin | RoleIsManager | RoleIsUser]
            case "create":
                permission_classes = [RoleIsUser]
            case "retrieve":
                permission_classes = [IsOwner | RoleIsAdmin | RoleIsManager]
            case "update":
                permission_classes = [RoleIsAdmin | RoleIsManager]
            case "destroy":
                permission_classes = [RoleIsAdmin | RoleIsManager]
            case "take":
                permission_classes = [RoleIsManager]
            case "reassign":
                permission_classes = [RoleIsAdmin]
            case _:
                permission_classes = []

        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["put"])
    def take(self, request, pk):
        ticket = self.get_object()

        serializer = TicketAssignSerializer(
            data={"manager_id": request.user.id}
        )  # noqa
        serializer.is_valid()
        ticket = serializer.assign(ticket)

        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=["put"])
    def reassign(self, request, pk):
        ticket = self.get_object()

        all_users = User.objects.all()
        manager_id = request.data["manager_id"]
        try:
            all_users.get(Q(id=manager_id) & Q(role=Role.MANAGER))
        except User.DoesNotExist:
            raise ValidationError({"error": "Enter manager ID"})

        serializer = TicketAssignSerializer(data={"manager_id": manager_id})
        serializer.is_valid()
        ticket = serializer.assign(ticket)

        return Response(TicketSerializer(ticket).data)


class MessageListCreateAPIView(ListCreateAPIView):
    serializer_class = TicketSerializer

    def get_queryset(self):
        return Message.objects.filter(
            Q(ticket__user=self.request.user)
            | Q(ticket__manager=self.request.user),  # noqa
            ticket_id=self.kwargs[self.lookup_field],
        )
