from time import sleep

from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from config.celery import celery_app
from tickets.models import Message, Ticket
from tickets.permissions import (
    IsOwner,
    RoleIsAdmin,
    RoleIsManager,
    RoleIsUser,
    UserIsNewManager,
)
from tickets.serializers import (
    MessageSerializer,
    TicketAssignSerializer,
    TicketSerializer,
)
from users.constants import Role
from users.models import User


@celery_app.task
def send_email():
    print("📭 Sending email")
    sleep(10)
    print("✅ Email sent")


class TicketAPIViewSet(ModelViewSet):
    serializer_class = TicketSerializer

    def get_queryset(self):
        user = self.request.user
        all_tickets = Ticket.objects.all()

        send_email.delay()

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
                permission_classes = [RoleIsAdmin, UserIsNewManager]
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
        new_manager_id = request.data["new_manager"]

        serializer = TicketAssignSerializer(
            data={"manager_id": new_manager_id}
        )  # noqa
        serializer.is_valid()
        ticket = serializer.assign(ticket)

        return Response(TicketSerializer(ticket).data)


class MessageListCreateAPIView(ListCreateAPIView):
    serializer_class = MessageSerializer
    lookup_field = "ticket_id"

    def get_queryset(self):
        ticket = get_object_or_404(
            Ticket.objects.all(), id=self.kwargs[self.lookup_field]
        )
        if (
            ticket.user != self.request.user
            and ticket.manager != self.request.user  # noqa
        ):
            raise Http404

        messages = Message.objects.filter(
            ticket_id=self.kwargs[self.lookup_field]
        )  # noqa
        return messages

    @staticmethod
    def get_ticket(user: User, ticket_id: int) -> Ticket:
        """Get tickets for current user."""

        tickets = Ticket.objects.filter(Q(user=user) | Q(manager=user))
        return get_object_or_404(tickets, id=ticket_id)

    def post(self, request, ticket_id: int):
        self.get_ticket(request.user, ticket_id)
        payload = {"text": request.data["text"], "ticket": ticket_id}
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
