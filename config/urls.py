import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt


def filter_by_keys(source: dict, keys: list[str]) -> dict:
    filtered_data = {}
    for key, value in source.items():
        if key in keys:
            filtered_data[key] = value
    return filtered_data


@dataclass
class Pokemon:
    id: int
    name: str
    height: int
    weight: int
    base_experience: int

    @classmethod
    def from_raw_data(cls, raw_data: dict) -> "Pokemon":
        filtered_data = filter_by_keys(
            raw_data,
            cls.__dataclass_fields__.keys(),
        )
        return cls(**filtered_data)


# ============================================
# Simulate the CACHE
# ============================================
TTL = timedelta(seconds=5)
POKEMONS: dict[str, list[Pokemon, datetime]] = {}


def get_pokemon_from_api(name: str) -> Pokemon:
    url = settings.POKEAPI_BASE_URL + f"/{name}"
    response = requests.get(url)
    raw_data = response.json()
    return Pokemon.from_raw_data(raw_data)


def _get_pokemon(name) -> Pokemon:
    """
    Take pokemon from the cache or
    fetch it from the API and then save it to the cache.
    """

    if name in POKEMONS:
        pokemon, created_at = POKEMONS[name]

        if datetime.now() > created_at + TTL:
            del POKEMONS[name]
            return _get_pokemon(name)
    else:
        pokemon: Pokemon = get_pokemon_from_api(name)
        POKEMONS[name] = [pokemon, datetime.now()]
    return pokemon


@csrf_exempt
def get_pokemon(request, name: str):
    if request.method == "GET":
        pokemon: Pokemon = _get_pokemon(name)
        return HttpResponse(
            content_type="application/json",
            content=json.dumps(asdict(pokemon)),
        )
    elif request.method == "DELETE":
        _del_pokemon(name)
        return JsonResponse({"message": "Pokemon was deleted successfully!"})


@csrf_exempt
def get_pokemon_for_mobile(request, name: str):
    if request.method == "GET":
        pokemon: Pokemon = _get_pokemon(name)
        result = filter_by_keys(
            asdict(pokemon),
            ["id", "name", "base_experience"],
        )
        return HttpResponse(
            content_type="application/json",
            content=json.dumps(result),
        )
    elif request.method == "DELETE":
        _del_pokemon(name)
        return JsonResponse({"message": "Pokemon was deleted successfully!"})


def get_pokemons_from_cache(request) -> dict:
    pokemons_cache = {}

    for name, pokemon_inf in POKEMONS.items():
        pokemons_cache[name] = asdict(pokemon_inf[0])

    return HttpResponse(
        content_type="application/json",
        content=json.dumps(pokemons_cache),
    )


def _del_pokemon(name: str):
    if name in POKEMONS:
        del POKEMONS[name]


def foo(request):
    return HttpResponse("<p>Here is the text of the Web page</p>")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("foo/", foo),
    path("api/pokemons/<str:name>/", get_pokemon),
    path("api/pokemons/mobile/<str:name>/", get_pokemon_for_mobile),
    path("api/pokemons/", get_pokemons_from_cache),
    path("api/pokemons/delete/<str:name>", _del_pokemon),
]
