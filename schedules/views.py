"""Страницы расписания: список занятий и карточка занятия.

Занятие связывает экскурсию и гида, поэтому на страницах выводятся
связанные объекты: schedule.excursion и schedule.guide.
"""

from django.shortcuts import render

from models import NotFoundError, get_schedule
from storage import load_all


def schedules(request):
    """Список занятий расписания с датой, гидом и загрузкой."""
    _, _, _, schedules_list = load_all()

    context = {"schedules": schedules_list}
    return render(request, "schedules/schedule_list.html", context)


def schedule_detail(request, schedule_id):
    """Карточка занятия: участники, свободные места, выручка и статус."""
    _, _, _, schedules_list = load_all()

    try:
        schedule = get_schedule(schedules_list, schedule_id)
    except NotFoundError:
        context = {
            "message": "Занятие не найдено",
            "hint": "Занятия с таким идентификатором нет в расписании.",
            "list_url": "schedules:list",
        }
        return render(request, "not_found.html", context, status=404)

    context = {"schedule": schedule}
    return render(request, "schedules/schedule_detail.html", context)
