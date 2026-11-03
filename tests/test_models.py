"""Тесты моделей: поля, связи, методы и вычисляемые свойства."""

from datetime import date, time
from decimal import Decimal

import pytest

from excursions.models import Excursion
from guides.models import Guide
from routes.models import Route
from schedules.models import Schedule

pytestmark = pytest.mark.django_db


def test_guide_str_and_languages(guide):
    """Строковое представление и разбор языков."""
    assert str(guide) == "Анна Смирнова"
    assert guide.languages_list == ["русский", "английский"]
    assert guide.knows_languages(["русский"])
    assert not guide.knows_languages(["французский"])


def test_route_str(route):
    """Маршрут печатается с длительностью и сложностью."""
    assert "Исторический центр" in str(route)
    assert "2.5" in str(route)
    assert route.required_languages_list == ["русский", "английский"]


def test_excursion_str_and_duration(excursion, route):
    """Экскурсия связана с маршрутом и берёт у него длительность."""
    assert str(excursion) == "Знакомство с городом (Исторический центр)"
    assert excursion.duration_hours == route.duration_hours
    assert excursion.is_family is False


def test_excursion_capacity(excursion):
    """Проверка вместимости экскурсии."""
    assert excursion.is_suitable_for(4)
    assert excursion.is_suitable_for(15)
    assert not excursion.is_suitable_for(0)
    assert not excursion.is_suitable_for(16)


def test_excursion_total_price(excursion):
    """Стоимость группы: базовая цена и скидка от шести человек."""
    assert excursion.total_price(4) == Decimal("7200")
    assert excursion.total_price(6) == Decimal("9720")


def test_excursion_total_price_error(excursion):
    """Слишком большая группа — понятная ошибка."""
    with pytest.raises(ValueError):
        excursion.total_price(20)


def test_family_excursion_child_price(route):
    """В семейной экскурсии детям половина цены."""
    family = Excursion.objects.create(
        title="Детская прогулка",
        route=route,
        kind="семейная экскурсия",
        base_price=Decimal("1200.00"),
        max_participants=10,
        min_age=4,
    )
    assert family.is_family
    assert family.price_per_person(participant_age=10) == Decimal("600.00")
    assert family.price_per_person(participant_age=18) == Decimal("1200.00")


def test_schedule_str_and_relations(schedule, guide, excursion):
    """Занятие связано с экскурсией и гидом, печатает дату и время."""
    assert "2026-03-10" in str(schedule)
    assert "10:00" in str(schedule)
    assert schedule.excursion == excursion
    assert schedule.guide == guide
    assert schedule.excursion.route == excursion.route


def test_schedule_calculated_fields(schedule):
    """Свободные места, выручка и заполняемость считаются свойствами."""
    assert schedule.free_seats == 7
    assert schedule.revenue == Decimal("14400.00")
    assert schedule.fill_percent == 53
    assert schedule.is_cancelled is False


def test_schedule_cancel_and_done(schedule):
    """Смена статуса сохраняется в базе."""
    schedule.cancel()
    schedule.refresh_from_db()
    assert schedule.status == "отменена"
    assert schedule.is_cancelled is True

    schedule.mark_done()
    schedule.refresh_from_db()
    assert schedule.status == "проведена"


def test_models_meta_ordering():
    """Сортировка по умолчанию задана в Meta."""
    assert Guide._meta.ordering == ["name"]
    assert Route._meta.ordering == ["name"]
    assert Excursion._meta.ordering == ["title"]
    assert Schedule._meta.ordering == ["date", "start_time"]


def test_schedule_default_status(guide, excursion):
    """По умолчанию занятие запланировано."""
    schedule = Schedule.objects.create(
        excursion=excursion,
        guide=guide,
        date=date(2026, 4, 1),
        start_time=time(12, 30),
    )
    assert schedule.status == "запланирована"
    assert schedule.booked == 0
    assert schedule.free_seats == 15
