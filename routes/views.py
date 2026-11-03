"""Страницы маршрутов: список с фильтрами и карточка маршрута."""

from django.db.models import Count
from django.shortcuts import render

from routes.models import DIFFICULTIES, Route

SORT_FIELDS = {
    "name": "name",
    "duration": "-duration_hours",
    "distance": "-distance_km",
}


def routes(request):
    """Список маршрутов: поиск, фильтр по сложности, сортировка."""
    queryset = Route.objects.annotate(excursions_count=Count("excursions"))

    query = request.GET.get("q", "").strip()
    difficulty = request.GET.get("difficulty", "").strip()
    sort = request.GET.get("sort", "name")

    if query:
        queryset = queryset.filter(name__icontains=query)
    if difficulty:
        queryset = queryset.filter(difficulty=difficulty)

    queryset = queryset.order_by(SORT_FIELDS.get(sort, "name"))

    context = {
        "routes": queryset,
        "query": query,
        "difficulty": difficulty,
        "sort": sort,
        "difficulties": [value for value, _ in DIFFICULTIES],
    }
    return render(request, "routes/route_list.html", context)


def route_detail(request, route_slug):
    """Карточка маршрута и экскурсии, которые по нему проводятся."""
    try:
        route = Route.objects.get(slug=route_slug)
    except Route.DoesNotExist:
        context = {
            "message": "Маршрут не найден",
            "hint": "Маршрута с таким идентификатором нет в справочнике.",
            "list_url": "routes:list",
        }
        return render(request, "not_found.html", context, status=404)

    context = {
        "route": route,
        "excursions": (
            route.excursions
            .annotate(schedules_count=Count("schedules"))
            .order_by("title")
        ),
    }
    return render(request, "routes/route_detail.html", context)
