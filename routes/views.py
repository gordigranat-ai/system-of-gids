"""Страницы маршрутов: список и карточка маршрута."""

from django.shortcuts import render

from models import NotFoundError, get_route
from storage import load_excursions, load_routes


def routes(request):
    """Список маршрутов с продолжительностью и сложностью."""
    context = {"routes": load_routes()}
    return render(request, "routes/route_list.html", context)


def route_detail(request, route_id):
    """Карточка маршрута и экскурсии, которые по нему проводятся."""
    routes_list = load_routes()

    try:
        route = get_route(routes_list, route_id)
    except NotFoundError:
        context = {
            "message": "Маршрут не найден",
            "hint": "Маршрута с таким идентификатором нет в справочнике.",
            "list_url": "routes:list",
        }
        return render(request, "not_found.html", context, status=404)

    excursions_list = load_excursions(routes_list)
    context = {
        "route": route,
        "excursions": [item for item in excursions_list
                       if item.route.id == route.id],
    }
    return render(request, "routes/route_detail.html", context)
