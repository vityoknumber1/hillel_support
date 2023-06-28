from rest_framework import serializers

from tickets.models import Ticket


class TicketSerializer(serializers.ModelField):
    user = serializers.HiddenField(default=1)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "text",
            "visibility",
            "status",
            "user",
            "manager",
        ]
        read_only_fields = ["visibility", "manager"]


class TicketAssignSerializer(serializers.Serializer):
    manager_id = serializers.IntegerField()

    def validate_manager_id(self, manager_id):
        return manager_id

    def assign(self, ticket: Ticket) -> Ticket:
        ticket.manager_id = self.validated_data["manager_id"]
        ticket.save()

        return ticket
