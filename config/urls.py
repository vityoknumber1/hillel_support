from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def foo(request):
    return HttpResponse("<p>Here is the text of the Web page</p>")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("foo/", foo),
]
