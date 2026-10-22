"""Страницы гидов: список, поиск свободных гидов и карточка гида.

Данные берутся из базы SQLite через db.repository: там SQL-запросы
и сборка объектов классов ПР3.
"""

from django.shortcuts import render

from db.repository import (
    get_guide,
    list_available_guides,
    list_guides,
    list_schedules_by_guide,
)


def guides(request):
    """Список гидов с языками и статусом работы."""
    context = {"guides": list_guides()}
    return render(request, "guides/guide_list.html", context)


def available_guides(request):
    """Гиды, свободные на выбранную дату.

    Дата приходит из формы методом GET: /guides/available/?date=2026-03-10.
    Если дата не указана, запрос к базе не выполняется.
    """
    schedule_date = request.GET.get("date")
    context = {"schedule_date": schedule_date, "guides": []}

    if schedule_date:
        context["guides"] = list_available_guides(schedule_date)

    return render(request, "guides/available.html", context)


def guide_detail(request, guide_id):
    """Карточка гида и его занятия в расписании."""
    guide = get_guide(guide_id)

    if guide is None:
        context = {
            "message": "Гид не найден",
            "hint": "Гида с таким идентификатором нет в справочнике.",
            "list_url": "guides:list",
        }
        return render(request, "not_found.html", context, status=404)

    context = {
        "guide": guide,
        "schedules": list_schedules_by_guide(guide_id),
    }
    return render(request, "guides/guide_detail.html", context)
