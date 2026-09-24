"""Тесты проекта.

Проверяем объекты классов, правила предметной области и сохранение данных.
Запуск: python -m pytest
"""

import os
from datetime import date

import pytest

from models import (
    CapacityError,
    DuplicateError,
    Excursion,
    FamilyExcursion,
    Guide,
    Route,
    Schedule,
    StorageError,
    ValidationError,
    add_guide,
    add_route,
    book_seats,
    cancel_schedule,
    create_excursion,
    create_guide,
    create_route,
    create_schedule,
    filter_excursions_by_price,
    filter_guides_by_language,
    get_excursion,
    get_guide,
    is_guide_available,
    search_guides,
)
from storage import load_guides, load_schedules, save_guides, save_schedules
from utils import parse_date, pluralize, split_list

TEST_DATE = date(2026, 3, 10)


def make_route():
    """Маршрут, по которому дальше создаём экскурсии."""
    return create_route([], "Исторический центр", 2.5, "лёгкий",
                        "Прогулка по центру", 3.5, ["русский", "английский"])


# --- гиды -----------------------------------------------------------------

def test_guide_creation_and_str():
    guide = Guide(1, "Анна Смирнова", "городская экскурсия", ["русский"], 7, 4.8)
    assert guide.id == 1
    assert guide.name == "Анна Смирнова"
    assert "городская экскурсия" in str(guide)


def test_guide_knows_languages_and_status():
    guide = Guide(1, "Анна", "городская экскурсия", ["русский", "английский"])
    assert guide.knows_languages(["русский"])
    assert not guide.knows_languages(["немецкий"])
    assert guide.get_status() == "Гид свободен и может провести экскурсию"
    assert guide.get_status(is_busy=True) == "Гид занят в указанное время"


def test_guide_from_data_and_checks():
    guide = Guide.from_data({
        "id": 3,
        "name": "Мария Ковалёва",
        "specialization": "природная экскурсия",
        "languages": ["русский"],
    })
    assert guide.id == 3

    guides = []
    with pytest.raises(ValidationError):
        add_guide(guides, Guide(1, "", "городская экскурсия", ["русский"]))
    create_guide(guides, "Анна", "городская экскурсия", ["русский"])
    with pytest.raises(DuplicateError):
        add_guide(guides, Guide(2, "анна", "городская экскурсия", ["русский"]))


def test_search_and_filter_guides():
    guides = [
        Guide(1, "Анна Смирнова", "городская экскурсия", ["русский", "английский"]),
        Guide(2, "Игорь Петров", "музейная экскурсия", ["русский"]),
    ]
    assert len(search_guides(guides, "петр")) == 1
    assert len(filter_guides_by_language(guides, "английский")) == 1
    assert get_guide(guides, 1).name == "Анна Смирнова"


# --- маршруты и экскурсии -------------------------------------------------

def test_route_creation():
    route = Route(1, "Парковый", 4.0, "средний", "Прогулка", 8.4, ["русский"])
    assert route.name == "Парковый"
    assert route.is_suitable_duration(5)
    assert Route.validate_difficulty("сложный")


def test_add_route_checks_data():
    routes = []
    with pytest.raises(ValidationError):
        add_route(routes, Route(1, "Маршрут", 0, "лёгкий"))
    create_route(routes, "Исторический центр", 2.5, "лёгкий")
    with pytest.raises(DuplicateError):
        create_route(routes, "Исторический центр", 3, "средний")


def test_excursion_links_to_route_and_price():
    route = make_route()
    excursion = Excursion(1, "Знакомство с городом", route, 15, 1000.0)
    assert excursion.route is route
    assert excursion.duration_hours == 2.5
    assert excursion.total_price(2, 30) == 2000.0
    assert excursion.total_price(6, 30) == 5400.0  # групповая скидка 10 %
    with pytest.raises(CapacityError):
        excursion.total_price(20, 30)


def test_family_excursion_discount():
    route = make_route()
    family = FamilyExcursion(1, "Детская прогулка", route, 20, 1200.0, min_age=4)
    ordinary = Excursion(2, "Обычная", route, 20, 1200.0)

    assert family.kind == "семейная экскурсия"
    assert family.price_per_person(10) == 600.0
    assert family.price_per_person(30) == 1200.0
    # один метод, а результат разный — полиморфизм
    assert family.total_price(2, 10) != ordinary.total_price(2, 10)


def test_filter_excursions_by_price():
    route = make_route()
    excursions = [
        create_excursion([], "Знакомство с городом", route, 1800.0, 15),
        create_excursion([], "Вкус города", route, 3200.0, 10),
    ]
    assert len(filter_excursions_by_price(excursions, 2000.0)) == 1
    assert get_excursion(excursions, 1).title == "Знакомство с городом"


# --- расписание -----------------------------------------------------------

def make_project():
    """Два гида, маршрут, экскурсия и пустое расписание."""
    guides = [
        Guide(1, "Анна Смирнова", "городская экскурсия", ["русский", "английский"]),
        Guide(2, "Игорь Петров", "музейная экскурсия", ["русский"]),
    ]
    route = make_route()
    excursion = create_excursion([], "Знакомство с городом", route, 1800.0, 15)
    return guides, excursion, []


def test_schedule_creation():
    guides, excursion, schedules = make_project()
    schedule = create_schedule(schedules, excursion, guides[0], TEST_DATE, "10:00")
    assert schedule.excursion is excursion
    assert schedule.guide is guides[0]
    assert schedule.date == "2026-03-10"
    assert schedule.free_seats == 15


def test_schedule_checks_languages():
    guides, excursion, schedules = make_project()
    # Игорь знает только русский, а маршрут требует ещё английский
    with pytest.raises(ValidationError):
        create_schedule(schedules, excursion, guides[1], TEST_DATE, "10:00")


def test_busy_guide():
    guides, excursion, schedules = make_project()
    create_schedule(schedules, excursion, guides[0], TEST_DATE, "10:00")
    with pytest.raises(DuplicateError):
        create_schedule(schedules, excursion, guides[0], TEST_DATE, "10:00")
    with pytest.raises(Exception):
        create_schedule(schedules, excursion, guides[0], TEST_DATE, "11:00")
    assert not is_guide_available(schedules, guides[0], TEST_DATE, "11:00")
    assert is_guide_available(schedules, guides[0], TEST_DATE, "15:00")


def test_booking_and_cancelling():
    guides, excursion, schedules = make_project()
    schedule = create_schedule(schedules, excursion, guides[0], TEST_DATE, "10:00")

    schedule.book_seats(5)
    assert schedule.booked == 5
    assert schedule.revenue == 9000.0

    with pytest.raises(CapacityError):
        schedule.book_seats(16)

    schedule.cancel_seats(2)
    assert schedule.booked == 3

    book_seats(schedules, schedule.id, 2)
    assert schedule.booked == 5


def test_cancel_schedule_frees_guide():
    guides, excursion, schedules = make_project()
    schedule = create_schedule(schedules, excursion, guides[0], TEST_DATE, "10:00")
    cancel_schedule(schedules, schedule.id)

    assert schedule.is_cancelled
    assert schedule.status_text == "Занятие отменено"
    # отменённое занятие время гида не занимает
    assert is_guide_available(schedules, guides[0], TEST_DATE, "10:00")


# --- вспомогательные функции и файлы --------------------------------------

def test_parse_date_and_split_list():
    assert parse_date("15.09.2026") == date(2026, 9, 15)
    assert parse_date("2026-09-15") == date(2026, 9, 15)
    assert split_list("русский, английский, ") == ["русский", "английский"]
    forms = ("человек", "человека", "человек")
    assert pluralize(1, forms) == "человек"
    assert pluralize(3, forms) == "человека"


def test_save_and_load_guides():
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "guides.json")

    guides = [Guide(1, "Анна Смирнова", "городская экскурсия", ["русский"], 7, 4.8)]
    assert save_guides(guides, path) == 1

    restored = load_guides(path)
    assert isinstance(restored[0], Guide)
    assert restored[0].name == "Анна Смирнова"


def test_schedule_links_in_file():
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "schedules.json")

    guide = Guide(1, "Анна", "городская экскурсия", ["русский"])
    route = make_route()
    excursion = create_excursion([], "Знакомство с городом", route, 1800.0, 15)
    schedules = [Schedule(1, excursion, guide, TEST_DATE, "10:00", booked=4)]
    save_schedules(schedules, path)

    restored = load_schedules([excursion], [guide], path)
    assert restored[0].excursion is excursion
    assert restored[0].guide is guide
    assert restored[0].booked == 4


def test_broken_file():
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "broken.json")
    with open(path, "w", encoding="utf-8") as file:
        file.write("{это не json")

    with pytest.raises(StorageError):
        load_guides(path)
