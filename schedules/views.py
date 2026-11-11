"""Страницы расписания: список, активные занятия, статистика, карточка.

Фильтр списка работает через `ScheduleFilterForm` (forms.Form), а создание
и редактирование занятия — через `ScheduleForm` (ModelForm). Отмена
занятия выполняется POST-запросом и меняет статус, не удаляя запись.
"""

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, DecimalField, F, FloatField, Q, Sum
from django.db.models.functions import Cast, Round
from django.shortcuts import redirect, render

from excursions.models import Excursion
from guides.models import Guide
from schedules.forms import ScheduleFilterForm, ScheduleForm
from schedules.models import Schedule, ScheduleStatus

PAGE_SIZE = 5

REVENUE_FIELD = DecimalField(max_digits=12, decimal_places=2)


def _find_schedule(schedule_id):
    """Найти занятие или вернуть None, если такого нет."""
    return Schedule.objects.with_related().filter(pk=schedule_id).first()


def _not_found(request):
    """Страница 404 для несуществующего занятия."""
    context = {
        "message": "Занятие не найдено",
        "hint": "Занятия с таким идентификатором нет в расписании.",
        "list_url": "schedules:list",
    }
    return render(request, "not_found.html", context, status=404)


def schedules(request):
    """Список занятий: фильтр из формы, сортировка и постраничный вывод."""
    form = ScheduleFilterForm(request.GET or None)
    queryset = Schedule.objects.with_related()

    if form.is_valid():
        queryset = form.filter_queryset(queryset)
    else:
        # Некорректные параметры не ломают страницу: показываем все занятия,
        # а форма выводит сообщения об ошибках.
        queryset = queryset.order_by("date", "start_time")

    paginator = Paginator(queryset, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)

    context = {
        "form": form,
        "page_obj": page_obj,
        "schedules": page_obj,
        "querystring": params.urlencode(),
    }
    return render(request, "schedules/schedule_list.html", context)


def schedule_create(request):
    """Создание занятия: GET — форма, POST — проверка и сохранение."""
    if request.method == "POST":
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save()
            messages.success(
                request,
                f"Занятие на {schedule.date} добавлено в расписание.",
            )
            return redirect("schedules:detail", schedule_id=schedule.pk)
    else:
        form = ScheduleForm()

    context = {"form": form, "is_edit": False}
    return render(request, "schedules/schedule_form.html", context)


def schedule_edit(request, schedule_id):
    """Редактирование существующего занятия."""
    schedule = _find_schedule(schedule_id)
    if schedule is None:
        return _not_found(request)

    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, "Изменения сохранены.")
            return redirect("schedules:detail", schedule_id=schedule.pk)
    else:
        form = ScheduleForm(instance=schedule)

    context = {"form": form, "schedule": schedule, "is_edit": True}
    return render(request, "schedules/schedule_form.html", context)


def schedule_cancel(request, schedule_id):
    """Отмена занятия: подтверждение на GET, изменение статуса на POST."""
    schedule = _find_schedule(schedule_id)
    if schedule is None:
        return _not_found(request)

    if request.method == "POST":
        schedule.cancel()
        messages.success(request, "Занятие отменено.")
        return redirect("schedules:detail", schedule_id=schedule.pk)

    context = {"schedule": schedule}
    return render(request, "schedules/schedule_cancel.html", context)


def active_schedules(request):
    """Занятия, которые не отменены: их ещё предстоит провести."""
    context = {"schedules": Schedule.objects.with_related().active()}
    return render(request, "schedules/active.html", context)


def statistics(request):
    """Статистика по статусам, гидам и экскурсиям через annotate/aggregate."""
    totals = Schedule.objects.aggregate(
        schedules=Count("id"),
        active=Count("id", filter=Q(status=ScheduleStatus.ACTIVE)),
        completed=Count("id", filter=Q(status=ScheduleStatus.COMPLETED)),
        cancelled=Count("id", filter=Q(status=ScheduleStatus.CANCELLED)),
        booked_total=Sum(
            "booked",
            filter=~Q(status=ScheduleStatus.CANCELLED),
        ),
        revenue=Sum(
            F("booked") * F("excursion__base_price"),
            filter=~Q(status=ScheduleStatus.CANCELLED),
            output_field=REVENUE_FIELD,
        ),
    )

    by_guide = Guide.objects.annotate(
        schedules_count=Count(
            "schedules",
            filter=~Q(schedules__status=ScheduleStatus.CANCELLED),
        ),
        booked_total=Sum(
            "schedules__booked",
            filter=~Q(schedules__status=ScheduleStatus.CANCELLED),
        ),
    ).order_by("-schedules_count", "name")

    by_excursion = (
        Excursion.objects.annotate(
            schedules_count=Count(
                "schedules",
                filter=~Q(schedules__status=ScheduleStatus.CANCELLED),
            ),
            booked_total=Sum(
                "schedules__booked",
                filter=~Q(schedules__status=ScheduleStatus.CANCELLED),
            ),
            revenue=Sum(
                F("schedules__booked") * F("base_price"),
                filter=~Q(schedules__status=ScheduleStatus.CANCELLED),
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
    schedule = _find_schedule(schedule_id)
    if schedule is None:
        return _not_found(request)

    context = {"schedule": schedule}
    return render(request, "schedules/schedule_detail.html", context)
