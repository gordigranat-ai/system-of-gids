"""Страницы гидов: список и карточка отдельного гида.

HTML формируют шаблоны, а view-функции только готовят контекст: данные
по-прежнему берутся средствами ПР3 (storage.py и классы из models.py).
"""

from django.shortcuts import render

from models import NotFoundError, get_guide
from storage import load_all, load_guides


def guides(request):
    """Список гидов с языками и статусом работы."""
    context = {"guides": load_guides()}
    return render(request, "guides/guide_list.html", context)


def guide_detail(request, guide_id):
    """Карточка гида и его занятия в расписании."""
    guides_list, _, _, schedules_list = load_all()

    try:
        guide = get_guide(guides_list, guide_id)
    except NotFoundError:
        context = {
            "message": "Гид не найден",
            "hint": "Гида с таким идентификатором нет в справочнике.",
            "list_url": "guides:list",
        }
        return render(request, "not_found.html", context, status=404)

    context = {
        "guide": guide,
        "schedules": [item for item in schedules_list
                      if item.guide.id == guide.id],
    }
    return render(request, "guides/guide_detail.html", context)
