import json
from random import choice, randint
from string import ascii_letters

from django.http import HttpResponse
from django.urls import path

from .models import Message, Request, User

# *****************************************************
# All roles are hardcoded instead of beeing used in the database
# *****************************************************
ROLES = {
    "ADMIN": 1,
    "MANAGER": 2,
    "USER": 3,
}


def _get_random_string(size: int) -> str:
    return "".join([choice(ascii_letters) for _ in range(size)])


def create_random_email(lower_bound: int, upper_bound: int) -> str:
    email_prefix = _get_random_string(size=randint(lower_bound, upper_bound))
    email_affix = _get_random_string(size=randint(lower_bound, upper_bound))
    return "".join((email_prefix, "@", email_affix, ".com"))


def create_random_user(request):
    user = User.objects.create(
        username=_get_random_string(size=randint(5, 10)),
        email=create_random_email(5, 8),
        first_name=_get_random_string(size=randint(5, 10)),
        last_name=_get_random_string(size=randint(5, 10)),
        password=_get_random_string(size=randint(10, 20)),
        role=ROLES["USER"],
    )

    result = {
        "id": user.pk,
        "username": user.username,
        "email": user.email,
        "firstName": user.first_name,
        "lastName": user.last_name,
        "role": user.role,
    }

    return HttpResponse(
        content_type="application/json",
        content=json.dumps(result),
    )


def create_random_request(request):
    usual_user = User.objects.create(
        username=_get_random_string(size=randint(5, 10)),
        email=create_random_email(5, 8),
        first_name=_get_random_string(size=randint(5, 10)),
        last_name=_get_random_string(size=randint(5, 10)),
        password=_get_random_string(size=randint(10, 20)),
        role=ROLES["USER"],
    )

    manager = User.objects.create(
        username=_get_random_string(size=randint(5, 10)),
        email="support@gmail.com",
        first_name=_get_random_string(size=randint(5, 10)),
        last_name=_get_random_string(size=randint(5, 10)),
        password=_get_random_string(size=randint(10, 20)),
        role=ROLES["MANAGER"],
    )
    request_from_user = Request.objects.create(
        title=_get_random_string(size=randint(1, 100)),
        text=_get_random_string(size=randint(1, 1000)),
        visibility=True,
        status=randint(1, 3),
        user=usual_user,
        manager=manager,
    )

    result = {
        "id": request_from_user.pk,
        "title": request_from_user.title,
        "text": request_from_user.text,
        "visibility": request_from_user.visibility,
        "status": request_from_user.status,
        "user": {
            "id": request_from_user.user.pk,
            "username": request_from_user.user.username,
            "email": request_from_user.user.email,
            "firstName": request_from_user.user.first_name,
            "lastName": request_from_user.user.last_name,
            "role": request_from_user.user.role,
        },
        "manager": {
            "id": request_from_user.manager.pk,
            "username": request_from_user.manager.username,
            "email": request_from_user.manager.email,
            "firstName": request_from_user.manager.first_name,
            "lastName": request_from_user.manager.last_name,
            "role": request_from_user.manager.role,
        },
    }

    return HttpResponse(
        content_type="application/json",
        content=json.dumps(result),
    )


def create_random_message(request):
    usual_user = User.objects.create(
        username=_get_random_string(size=randint(5, 10)),
        email=create_random_email(5, 8),
        first_name=_get_random_string(size=randint(5, 10)),
        last_name=_get_random_string(size=randint(5, 10)),
        password=_get_random_string(size=randint(10, 20)),
        role=ROLES["USER"],
    )

    manager = User.objects.create(
        username=_get_random_string(size=randint(5, 10)),
        email="support@gmail.com",
        first_name=_get_random_string(size=randint(5, 10)),
        last_name=_get_random_string(size=randint(5, 10)),
        password=_get_random_string(size=randint(10, 20)),
        role=ROLES["MANAGER"],
    )

    request_from_user = Request.objects.create(
        title=_get_random_string(size=randint(1, 100)),
        text=_get_random_string(size=randint(1, 1000)),
        visibility=True,
        status=randint(1, 3),
        user=usual_user,
        manager=manager,
    )

    message = Message.objects.create(
        text=_get_random_string(size=randint(1, 1000)),
        user=usual_user,
        request=request_from_user,
    )

    result = {
        "text": message.text,
        "request": {
            "id": request_from_user.pk,
            "title": request_from_user.title,
            "text": request_from_user.text,
            "visibility": request_from_user.visibility,
            "status": request_from_user.status,
            "user": {
                "id": request_from_user.user.pk,
                "username": request_from_user.user.username,
                "email": request_from_user.user.email,
                "firstName": request_from_user.user.first_name,
                "lastName": request_from_user.user.last_name,
                "role": request_from_user.user.role,
            },
            "manager": {
                "id": request_from_user.manager.pk,
                "username": request_from_user.manager.username,
                "email": request_from_user.manager.email,
                "firstName": request_from_user.manager.first_name,
                "lastName": request_from_user.manager.last_name,
                "role": request_from_user.manager.role,
            },
        },
    }
    return HttpResponse(
        content_type="application/json",
        content=json.dumps(result),
    )


urlpatterns = [
    path("create-random-user/", create_random_user),
    path("create-random-request/", create_random_request),
    path("create-random-message/", create_random_message),
]
