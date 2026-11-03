"""Страницы экскурсий: список с фильтрами и карточка экскурсии."""

from decimal import Decimal, InvalidOperation

from django.db.models import Count
from django.shortcuts import render

from excursions.models import KINDS, Excursion

SORT_FIELDS = {
    "title": "title",
    "price": "-base_price",
    "participants": "-max_participants",
}


def excursions(request):
    """Список экскурсий: поиск, фильтр по виду и цене, сортировка."""
    queryset = Excursion.objects.select_related("route").annotate(
        schedules_count=Count("schedules"),
    )

    query = request.GET.get("q", "").strip()
    kind = request.GET.get("kind", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    sort = request.GET.get("sort", "title")

    if query:
        queryset = queryset.filter(title__icontains=query)
    if kind:
        queryset = queryset.filter(kind=kind)

    error = ""
    if max_price:
        try:
            price = Decimal(max_price)
        except InvalidOperation:
            error = "Цена должна быть числом."
        else:
            queryset = queryset.filter(base_price__lte=price)

    queryset = queryset.order_by(SORT_FIELDS.get(sort, "title"))

    context = {
        "excursions": queryset,
        "query": query,
        "kind": kind,
        "max_price": max_price,
        "sort": sort,
        "kinds": [value for value, _ in KINDS],
        "error": error,
    }
    return render(request, "excursions/excursion_list.html", context)


def excursion_detail(request, excursion_id):
    """Карточка экскурсии: маршрут, цена, вместимость и стоимость группы."""
    try:
        excursion = Excursion.objects.select_related("route").get(
            pk=excursion_id,
        )
    except Excursion.DoesNotExist:
        context = {
            "message": "Экскурсия не найдена",
            "hint": "Экскурсии с таким идентификатором нет в справочнике.",
            "list_url": "excursions:list",
        }
        return render(request, "not_found.html", context, status=404)

    context = {
        "excursion": excursion,
        # Стоимость считает метод модели — в шаблоне только вывод.
        "group_price": excursion.total_price(4),
        "schedules": (
            excursion.schedules
            .select_related("guide")
            .order_by("date", "start_time")
        ),
    }
    return render(request, "excursions/excursion_detail.html", context)
