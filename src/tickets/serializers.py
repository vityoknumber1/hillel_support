from rest_framework import serializers

from tickets.models import Ticket


class TicketSerializer(serializers.ModelField):
    user = serializers.HiddenField(default=1)

    class Meta:
        model = Ticket
        fields = ["id", "title", "text", "visibility", "status", "user"]
        read_only_fields = ["visibility"]

    def validate(self, attrs: dict):
        return attrs

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
