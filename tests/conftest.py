"""Общие настройки тестов и фикстуры с данными проекта.

Django-базу для тестов создаёт pytest-django: тесты, которым нужны
модели, помечаются маркером django_db или получают фикстуру db.
"""

import os
import sys
from datetime import date, time
from decimal import Decimal

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Отладочный режим нужен, чтобы шаблоны показывали свои ошибки.
os.environ.setdefault("DJANGO_DEBUG", "1")


@pytest.fixture()
def route(db):
    """Один маршрут для тестов."""
    from routes.models import Route

    return Route.objects.create(
        name="Исторический центр",
        description="Прогулка по главным площадям.",
        duration_hours=Decimal("2.5"),
        distance_km=Decimal("3.5"),
        difficulty="лёгкий",
        required_languages="русский, английский",
    )


@pytest.fixture()
def guide(db):
    """Один гид для тестов."""
    from guides.models import Guide

    return Guide.objects.create(
        name="Анна Смирнова",
        specialization="городская экскурсия",
        languages="русский, английский",
        experience_years=7,
        rating=Decimal("4.8"),
    )


@pytest.fixture()
def excursion(db, route):
    """Экскурсия по маршруту."""
    from excursions.models import Excursion

    return Excursion.objects.create(
        title="Знакомство с городом",
        route=route,
        kind="обычная экскурсия",
        base_price=Decimal("1800.00"),
        max_participants=15,
        min_age=0,
        languages="русский, английский",
    )


@pytest.fixture()
def schedule(db, excursion, guide):
    """Одно занятие в расписании."""
    from schedules.models import Schedule

    return Schedule.objects.create(
        excursion=excursion,
        guide=guide,
        date=date(2026, 3, 10),
        start_time=time(10, 0),
        booked=8,
        status="active",
        note="Группа туристов",
    )


@pytest.fixture()
def dataset(route, guide, excursion, schedule):
    """Весь набор данных одним словарём."""
    return {
        "route": route,
        "guide": guide,
        "excursion": excursion,
        "schedule": schedule,
    }


@pytest.fixture()
def many_schedules(db, excursion, guide):
    """Семь занятий — для проверки пагинации и сортировки."""
    from schedules.models import Schedule

    schedules = []
    for number in range(1, 8):
        schedules.append(Schedule.objects.create(
            excursion=excursion,
            guide=guide,
            date=date(2026, 3, number),
            start_time=time(10, 0),
            booked=number,
            status="active" if number % 2 else "completed",
        ))
    return schedules
