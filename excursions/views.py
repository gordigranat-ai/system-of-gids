"""Страницы экскурсий: список и карточка экскурсии.

Стоимость и скидки считают методы класса Excursion: в веб-слое логика
предметной области не повторяется.
"""

from django.shortcuts import render

from models import NotFoundError, get_excursion
from storage import load_excursions, load_routes


def excursions(request):
    """Список экскурсий с ценой и числом мест."""
    excursions_list = load_excursions(load_routes())

    context = {"excursions": excursions_list}
    return render(request, "excursions/excursion_list.html", context)


def excursion_detail(request, excursion_id):
    """Карточка экскурсии: маршрут, цена, вместимость и стоимость группы."""
    routes_list = load_routes()
    excursions_list = load_excursions(routes_list)

    try:
        excursion = get_excursion(excursions_list, excursion_id)
    except NotFoundError:
        context = {
            "message": "Экскурсия не найдена",
            "hint": "Экскурсии с таким идентификатором нет в справочнике.",
            "list_url": "excursions:list",
        }
        return render(request, "not_found.html", context, status=404)

    context = {
        "excursion": excursion,
        # Стоимость считает метод класса — в шаблоне только вывод.
        "group_price": excursion.total_price(4),
    }
    return render(request, "excursions/excursion_detail.html", context)
