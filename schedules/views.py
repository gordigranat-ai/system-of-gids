"""Страницы расписания: список, активные занятия, статистика, карточка.

Все данные получает Django ORM: filter(), exclude(), Q-объекты,
order_by(), select_related(), annotate(), aggregate() и Paginator.
"""

from datetime import date

from django.core.paginator import Paginator
from django.db.models import (
    Count,
    DecimalField,
    F,
    FloatField,
    Q,
    Sum,
)
from django.db.models.functions import Cast, Round
from django.shortcuts import render

from excursions.models import Excursion
from guides.models import Guide
from schedules.models import (
    STATUS_CANCELLED,
    STATUS_CHOICES,
    STATUS_DONE,
    STATUS_PLANNED,
    Schedule,
)

SORT_FIELDS = {
    "date": ("date", "start_time"),
    "date_desc": ("-date", "-start_time"),
    "booked": ("-booked", "date"),
    "excursion": ("excursion__title", "date"),
    "guide": ("guide__name", "date"),
}

STATUS_VALUES = [value for value, _ in STATUS_CHOICES]
ACTIVE_STATUSES = (STATUS_PLANNED, STATUS_DONE)
PAGE_SIZE = 5

REVENUE_FIELD = DecimalField(max_digits=12, decimal_places=2)


def _read_filters(request):
    """Собрать параметры фильтрации и сортировки из строки запроса."""
    return {
        "query": request.GET.get("q", "").strip(),
        "status": request.GET.get("status", "").strip(),
        "guide": request.GET.get("guide", "").strip(),
        "date_from": request.GET.get("date_from", "").strip(),
        "date_to": request.GET.get("date_to", "").strip(),
        "sort": request.GET.get("sort", "date"),
    }


def _apply_filters(queryset, filters):
    """Применить фильтры и сортировку; вернуть набор и текст ошибки."""
    error = ""

    if filters["query"]:
        queryset = queryset.filter(
            Q(excursion__title__icontains=filters["query"])
            | Q(guide__name__icontains=filters["query"])
        )

    if filters["status"] in STATUS_VALUES:
        queryset = queryset.filter(status=filters["status"])

    if filters["guide"]:
        if filters["guide"].isdigit():
            queryset = queryset.filter(guide_id=int(filters["guide"]))
        else:
            error = "Гида нужно выбрать из списка."

    try:
        if filters["date_from"]:
            queryset = queryset.filter(
                date__gte=date.fromisoformat(filters["date_from"]),
            )
        if filters["date_to"]:
            queryset = queryset.filter(
                date__lte=date.fromisoformat(filters["date_to"]),
            )
    except ValueError:
        error = "Даты должны быть в формате ГГГГ-ММ-ДД."

    queryset = queryset.order_by(*SORT_FIELDS.get(filters["sort"], SORT_FIELDS["date"]))
    return queryset, error


def _base_queryset():
    """Набор занятий со связанными объектами одним запросом."""
    return Schedule.objects.select_related(
        "excursion",
        "excursion__route",
        "guide",
    )


def schedules(request):
    """Список занятий: фильтры, сортировка и постраничный вывод."""
    filters = _read_filters(request)
    queryset, error = _apply_filters(_base_queryset(), filters)

    paginator = Paginator(queryset, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)

    context = {
        "page_obj": page_obj,
        "schedules": page_obj,
        "paginator": paginator,
        "querystring": params.urlencode(),
        "guides": Guide.objects.order_by("name"),
        "statuses": STATUS_CHOICES,
        "error": error,
        "filters": filters,
    }
    return render(request, "schedules/schedule_list.html", context)


def active_schedules(request):
    """Занятия, которые не отменены: их ещё предстоит провести."""
    queryset = (
        _base_queryset()
        .exclude(status=STATUS_CANCELLED)
        .order_by("date", "start_time")
    )
    context = {"schedules": queryset}
    return render(request, "schedules/active.html", context)


def statistics(request):
    """Статистика по статусам, гидам и экскурсиям через annotate/aggregate."""
    totals = Schedule.objects.aggregate(
        schedules=Count("id"),
        planned=Count("id", filter=Q(status=STATUS_PLANNED)),
        done=Count("id", filter=Q(status=STATUS_DONE)),
        cancelled=Count("id", filter=Q(status=STATUS_CANCELLED)),
        booked_total=Sum("booked", filter=Q(status__in=ACTIVE_STATUSES)),
        revenue=Sum(
            F("booked") * F("excursion__base_price"),
            filter=Q(status__in=ACTIVE_STATUSES),
            output_field=REVENUE_FIELD,
        ),
    )

    by_guide = Guide.objects.annotate(
        schedules_count=Count(
            "schedules",
            filter=Q(schedules__status__in=ACTIVE_STATUSES),
        ),
        booked_total=Sum(
            "schedules__booked",
            filter=Q(schedules__status__in=ACTIVE_STATUSES),
        ),
    ).order_by("-schedules_count", "name")

    by_excursion = (
        Excursion.objects.annotate(
            schedules_count=Count(
                "schedules",
                filter=Q(schedules__status__in=ACTIVE_STATUSES),
            ),
            booked_total=Sum(
                "schedules__booked",
                filter=Q(schedules__status__in=ACTIVE_STATUSES),
            ),
            revenue=Sum(
                F("schedules__booked") * F("base_price"),
                filter=Q(schedules__status__in=ACTIVE_STATUSES),
                output_field=REVENUE_FIELD,
            ),
        )
        .annotate(
            load_percent=Round(
                Cast(F("booked_total"), FloatField())
                * 100.0
                / (
                    Cast(F("schedules_count"), FloatField())
                    * Cast(F("max_participants"), FloatField())
                ),
                1,
            ),
        )
        .order_by("-revenue", "title")
    )

    context = {
        "totals": totals,
        "by_guide": by_guide,
        "by_excursion": by_excursion,
    }
    return render(request, "schedules/statistics.html", context)


def schedule_detail(request, schedule_id):
    """Карточка занятия: участники, свободные места, выручка и статус."""
    try:
        schedule = _base_queryset().get(pk=schedule_id)
    except Schedule.DoesNotExist:
        context = {
            "message": "Занятие не найдено",
            "hint": "Занятия с таким идентификатором нет в расписании.",
            "list_url": "schedules:list",
        }
        return render(request, "not_found.html", context, status=404)

    context = {"schedule": schedule}
    return render(request, "schedules/schedule_detail.html", context)
