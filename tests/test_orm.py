"""Тесты ORM-запросов: выборки, фильтры, связи, агрегаты, пагинация."""

from datetime import date

import pytest
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Q, Sum

from excursions.models import Excursion
from guides.models import Guide
from routes.models import Route
from schedules.models import Schedule

pytestmark = pytest.mark.django_db


def test_all_and_count(dataset):
    """Получение всех записей и подсчёт количества."""
    assert Guide.objects.count() == 1
    assert Route.objects.count() == 1
    assert Excursion.objects.count() == 1
    assert Schedule.objects.count() == 1
    assert list(Guide.objects.all()) == [dataset["guide"]]


def test_get_by_pk(dataset):
    """Получение одного объекта по первичному ключу."""
    guide = Guide.objects.get(pk=dataset["guide"].pk)
    assert guide.name == "Анна Смирнова"
    with pytest.raises(Guide.DoesNotExist):
        Guide.objects.get(pk=9999)


def test_filter_one_condition(many_schedules):
    """Фильтр по одному условию."""
    done = Schedule.objects.filter(status="completed")
    assert done.count() == 3


def test_filter_several_conditions(many_schedules):
    """Фильтр по нескольким условиям сразу."""
    selected = Schedule.objects.filter(status="completed", booked__gte=2)
    assert selected.count() == 3


def test_filter_by_related_field(many_schedules):
    """Фильтр по полю связанной модели."""
    assert Schedule.objects.filter(guide__name="Анна Смирнова").count() == 7
    assert Schedule.objects.filter(excursion__route__difficulty="лёгкий").count() == 7


def test_exclude(dataset):
    """Исключение записей по условию."""
    assert Schedule.objects.exclude(status="cancelled").count() == 1
    Schedule.objects.create(
        excursion=dataset["excursion"],
        guide=dataset["guide"],
        date=date(2026, 5, 1),
        start_time="09:00",
        status="cancelled",
    )
    assert Schedule.objects.exclude(status="cancelled").count() == 1
    assert Schedule.objects.count() == 2


def test_q_objects_or(many_schedules):
    """Составное условие через Q: «или» по двум полям."""
    result = Schedule.objects.filter(
        Q(status="completed") | Q(booked__gte=6),
    )
    assert result.count() >= 4


def test_search_icontains(dataset):
    """Поиск по строковому полю через icontains.

    В SQLite оператор LIKE сравнивает без учёта регистра только латиницу,
    поэтому кириллицу ищем с тем же регистром, что и в данных.
    """
    assert Guide.objects.filter(name__icontains="Анна").count() == 1
    assert Guide.objects.filter(name__icontains="Петров").count() == 0
    assert Guide.objects.filter(name__contains="Смирнова").count() == 1


def test_order_by_several_fields(many_schedules):
    """Сортировка по двум полям."""
    ordered = Schedule.objects.order_by("booked", "date")
    assert [item.booked for item in ordered] == [1, 2, 3, 4, 5, 6, 7]


def test_values_and_values_list(dataset):
    """Сокращённый набор полей через values() и values_list()."""
    row = Schedule.objects.values("date", "booked").get()
    assert row["booked"] == 8
    assert list(Guide.objects.values_list("name", flat=True)) == ["Анна Смирнова"]


def test_aggregate(many_schedules):
    """Агрегирование: сумма, среднее, максимум."""
    totals = Schedule.objects.aggregate(
        booked_total=Sum("booked"),
        average=Avg("booked"),
        maximum=Max("booked"),
    )
    assert totals["booked_total"] == 28
    assert totals["maximum"] == 7
    assert totals["average"] == 4


def test_annotate(many_schedules, guide):
    """Аннотирование: количество занятий у гида."""
    annotated = Guide.objects.annotate(
        schedules_count=Count("schedules"),
        booked_total=Sum("schedules__booked"),
    ).get(pk=guide.pk)
    assert annotated.schedules_count == 7
    assert annotated.booked_total == 28


def test_reverse_relation(dataset):
    """Обратная связь по related_name."""
    guide = dataset["guide"]
    assert guide.schedules.count() == 1
    assert dataset["route"].excursions.count() == 1
    assert dataset["excursion"].schedules.count() == 1


def test_select_related_reduces_queries(dataset, django_assert_num_queries):
    """select_related подтягивает связанные объекты одним запросом."""
    with django_assert_num_queries(1):
        schedule = Schedule.objects.select_related(
            "excursion",
            "guide",
        ).get(pk=dataset["schedule"].pk)
        assert schedule.excursion.title
        assert schedule.guide.name


def test_pagination(many_schedules):
    """Постраничный вывод через Paginator."""
    paginator = Paginator(Schedule.objects.order_by("date"), 5)
    first = paginator.page(1)
    second = paginator.page(2)

    assert paginator.count == 7
    assert paginator.num_pages == 2
    assert len(first.object_list) == 5
    assert len(second.object_list) == 2


def test_create_update_delete(db, guide, excursion):
    """Создание, изменение и удаление объекта через ORM."""
    schedule = Schedule.objects.create(
        excursion=excursion,
        guide=guide,
        date=date(2026, 6, 1),
        start_time="11:00",
        booked=2,
    )
    schedule.booked = 5
    schedule.save(update_fields=["booked"])
    schedule.refresh_from_db()
    assert schedule.booked == 5

    schedule.delete()
    assert Schedule.objects.count() == 0
