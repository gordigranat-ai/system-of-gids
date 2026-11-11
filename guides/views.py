"""Страницы гидов: список с поиском, свободные на дату, карточка.

Данные получаются через Django ORM: вместо SQL-запросов используются
менеджеры моделей, filter(), exclude(), order_by() и связи.
"""

from datetime import date

from django.contrib import messages
from django.shortcuts import redirect, render

from guides.forms import GuideForm
from guides.models import Guide
from schedules.models import Schedule, ScheduleStatus

SORT_FIELDS = {
    "name": "name",
    "rating": "-rating",
    "experience": "-experience_years",
}

BUSY_STATUSES = (ScheduleStatus.ACTIVE, ScheduleStatus.COMPLETED)


def _language_options():
    """Список языков для фильтра: собирается из поля languages."""
    languages = set()
    for value in Guide.objects.values_list("languages", flat=True):
        languages.update(
            item.strip() for item in value.split(",") if item.strip()
        )
    return sorted(languages)


def guides(request):
    """Список гидов: поиск по имени, фильтр по языку, сортировка."""
    queryset = Guide.objects.all()

    query = request.GET.get("q", "").strip()
    language = request.GET.get("language", "").strip()
    sort = request.GET.get("sort", "name")

    if query:
        queryset = queryset.filter(name__icontains=query)
    if language:
        queryset = queryset.filter(languages__icontains=language)

    queryset = queryset.order_by(SORT_FIELDS.get(sort, "name"))

    context = {
        "guides": queryset,
        "query": query,
        "language": language,
        "sort": sort,
        "languages": _language_options(),
    }
    return render(request, "guides/guide_list.html", context)


def available_guides(request):
    """Гиды, свободные на выбранную дату.

    Дата приходит из формы методом GET: /guides/available/?date=2026-03-10.
    Занятыми считаются гиды, у которых на эту дату есть занятие, кроме
    отменённых: отменённое занятие время гида не занимает.
    """
    raw_date = request.GET.get("date", "").strip()
    context = {
        "schedule_date": raw_date,
        "guides": Guide.objects.none(),
        "error": "",
    }

    if raw_date:
        try:
            day = date.fromisoformat(raw_date)
        except ValueError:
            context["error"] = "Дата должна быть в формате ГГГГ-ММ-ДД."
            return render(request, "guides/available.html", context)

        # Занятые гиды определяются подзапросом: exclude() с двумя условиями
        # по связи проверяет их отдельными EXISTS и даёт неверный результат,
        # поэтому сначала выбираем сами занятия, а потом исключаем их гидов.
        busy = Schedule.objects.filter(
            date=day,
            status__in=BUSY_STATUSES,
        )
        context["schedule_date"] = day.isoformat()
        context["guides"] = (
            Guide.objects.filter(is_active=True)
            .exclude(schedules__in=busy)
            .order_by("name")
        )

    return render(request, "guides/available.html", context)


def guide_detail(request, guide_id):
    """Карточка гида и его занятия в расписании."""
    try:
        guide = Guide.objects.get(pk=guide_id)
    except Guide.DoesNotExist:
        context = {
            "message": "Гид не найден",
            "hint": "Гида с таким идентификатором нет в справочнике.",
            "list_url": "guides:list",
        }
        return render(request, "not_found.html", context, status=404)

    context = {
        "guide": guide,
        "schedules": (
            guide.schedules
            .select_related("excursion", "excursion__route")
            .exclude(status=ScheduleStatus.CANCELLED)
            .order_by("date", "start_time")
        ),
    }
    return render(request, "guides/guide_detail.html", context)


def guide_edit(request, guide_id):
    """Редактирование гида, включая загрузку фотографии."""
    guide = Guide.objects.filter(pk=guide_id).first()
    if guide is None:
        context = {
            "message": "Гид не найден",
            "hint": "Гида с таким идентификатором нет в справочнике.",
            "list_url": "guides:list",
        }
        return render(request, "not_found.html", context, status=404)

    if request.method == "POST":
        form = GuideForm(request.POST, request.FILES, instance=guide)
        if form.is_valid():
            form.save()
            messages.success(request, "Данные гида сохранены.")
            return redirect("guides:detail", guide_id=guide.pk)
    else:
        form = GuideForm(instance=guide)

    context = {"form": form, "guide": guide}
    return render(request, "guides/guide_form.html", context)
