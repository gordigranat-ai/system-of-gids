"""Страницы маршрутов: список и карточка маршрута."""

from django.shortcuts import render

from db.repository import get_route, list_excursions_by_route, list_routes


def routes(request):
    """Список маршрутов с продолжительностью и сложностью."""
    context = {"routes": list_routes()}
    return render(request, "routes/route_list.html", context)


def route_detail(request, route_id):
    """Карточка маршрута и экскурсии, которые по нему проводятся."""
    route = get_route(route_id)

    if route is None:
        context = {
            "message": "Маршрут не найден",
            "hint": "Маршрута с таким идентификатором нет в справочнике.",
            "list_url": "routes:list",
        }
        return render(request, "not_found.html", context, status=404)

    context = {
        "route": route,
        "excursions": list_excursions_by_route(route_id),
    }
    return render(request, "routes/route_detail.html", context)
