from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.errors import SerializerError

User = get_user_model()


class UserCreateRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class UserCreateResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class LoginResponseSerializer(serializers.ModelSerializer):
    def post(self, request):
        login_request_serializer = LoginRequestSerializer(data=request.data)

        if not login_request_serializer.is_valid():
            raise SerializerError(login_request_serializer)

        return "Login successful"
