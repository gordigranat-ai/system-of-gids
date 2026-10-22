"""Страницы экскурсий: список и карточка экскурсии.

Стоимость и скидки считают методы класса Excursion: в веб-слое логика
предметной области не повторяется.
"""

from django.shortcuts import render

from db.repository import get_excursion, list_excursions


def excursions(request):
    """Список экскурсий с ценой и числом мест."""
    context = {"excursions": list_excursions()}
    return render(request, "excursions/excursion_list.html", context)


def excursion_detail(request, excursion_id):
    """Карточка экскурсии: маршрут, цена, вместимость и стоимость группы."""
    excursion = get_excursion(excursion_id)

    if excursion is None:
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
