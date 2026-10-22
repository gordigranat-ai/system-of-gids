"""Тесты веб-интерфейса.

Проверяем то, что требуют ПР5–ПР7: каждый маршрут связан с view-функцией,
страницы открываются с кодом 200, несуществующие объекты и адреса дают
код 404, а данные берутся из базы проекта. Идентификаторы объектов
читаются из данных, поэтому тесты не зависят от конкретных записей.
"""

import pytest
from django.test import Client

from db.repository import (
    list_excursions,
    list_guides,
    list_routes,
    list_schedules,
)


@pytest.fixture()
def client():
    """Клиент Django, который выполняет запросы без запуска сервера."""
    return Client()


@pytest.fixture()
def data():
    """Данные проекта, разложенные по видам."""
    return {
        "guides": list_guides(),
        "routes": list_routes(),
        "excursions": list_excursions(),
        "schedules": list_schedules(),
    }


def test_home_page_opens(client):
    """Главная страница открывается и содержит название проекта."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Сервис управления гидами" in response.content.decode()


def test_list_pages_open(client):
    """Все списки предметной области открываются."""
    for url in ("/guides/", "/routes/", "/excursions/", "/schedules/"):
        response = client.get(url)
        assert response.status_code == 200, url


def test_navigation_links_present(client):
    """Навигация есть на каждой странице и ведёт в четыре раздела."""
    html = client.get("/").content.decode()
    for url in ("/guides/", "/routes/", "/excursions/", "/schedules/"):
        assert f'href="{url}"' in html


def test_guide_detail_opens(client, data):
    """Страница существующего гида показывает его имя."""
    guide = data["guides"][0]
    response = client.get(f"/guides/{guide.id}/")
    assert response.status_code == 200
    assert guide.name in response.content.decode()


def test_route_detail_opens(client, data):
    """Страница существующего маршрута показывает его название."""
    route = data["routes"][0]
    response = client.get(f"/routes/{route.id}/")
    assert response.status_code == 200
    assert route.name in response.content.decode()


def test_excursion_detail_opens(client, data):
    """Страница существующей экскурсии показывает её название."""
    excursion = data["excursions"][0]
    response = client.get(f"/excursions/{excursion.id}/")
    assert response.status_code == 200
    assert excursion.title in response.content.decode()


def test_schedule_detail_opens(client, data):
    """Страница занятия показывает дату и гида."""
    schedule = data["schedules"][0]
    response = client.get(f"/schedules/{schedule.id}/")
    assert response.status_code == 200
    html = response.content.decode()
    assert schedule.date in html
    assert schedule.guide.name in html


def test_missing_objects_return_404(client):
    """Несуществующие идентификаторы дают код 404."""
    for url in (
        "/guides/9999/",
        "/routes/9999/",
        "/excursions/9999/",
        "/schedules/9999/",
    ):
        response = client.get(url)
        assert response.status_code == 404, url


def test_unknown_address_returns_404(client):
    """Адрес без маршрута обрабатывается страницей 404."""
    response = client.get("/nonexistent/")
    assert response.status_code == 404


def test_pages_use_bootstrap(client):
    """Страницы подключают Bootstrap и содержат общий каркас документа."""
    html = client.get("/").content.decode()
    assert "bootstrap" in html
    assert "<title>" in html


def test_guide_status_badge(client, data):
    """В списке гидов статус работы выводится бейджем."""
    response = client.get("/guides/")
    html = response.content.decode()
    assert response.status_code == 200
    assert "badge" in html


def test_pages_extend_base_template(client):
    """Страницы наследуют базовый шаблон: один документ и общий подвал."""
    html = client.get("/schedules/").content.decode()
    assert html.count("<!DOCTYPE html>") == 1
    assert 'id="current-year"' in html
    assert "Экскурсионное бюро" in html


def test_static_files_are_found():
    """Статические файлы проекта находятся системой staticfiles."""
    from django.contrib.staticfiles import finders

    for name in (
        "homepage/css/style.css",
        "homepage/js/main.js",
        "homepage/img/logo.png",
    ):
        assert finders.find(name) is not None, name


def test_available_guides_page_opens(client):
    """Поиск свободных гидов: форма без даты и результат с датой."""
    empty = client.get("/guides/available/")
    assert empty.status_code == 200

    response = client.get("/guides/available/", {"date": "2026-03-10"})
    html = response.content.decode()
    assert response.status_code == 200
    assert "2026-03-10" in html


def test_active_schedules_page_opens(client):
    """Страница активных занятий открывается."""
    response = client.get("/schedules/active/")
    assert response.status_code == 200
    assert "Активные занятия" in response.content.decode()


def test_active_page_excludes_cancelled(client, data):
    """Отменённые занятия не попадают в список активных."""
    cancelled = [item for item in data["schedules"] if item.is_cancelled]
    if not cancelled:
        pytest.skip("в базе нет отменённых занятий")

    html = client.get("/schedules/active/").content.decode()
    for item in cancelled:
        assert f"/schedules/{item.id}/" not in html


def test_statistics_page_shows_sql_data(client):
    """Страница статистики выводит результат SQL-запросов."""
    response = client.get("/schedules/statistics/")
    html = response.content.decode()

    assert response.status_code == 200
    assert "Занятия по гидам" in html
    assert "Выручка и заполняемость экскурсий" in html


def test_related_objects_are_linked(data):
    """Данные из базы сохраняют связи между объектами."""
    route_ids = {route.id for route in data["routes"]}
    excursion_ids = {item.id for item in data["excursions"]}
    guide_ids = {guide.id for guide in data["guides"]}

    assert data["excursions"], "в базе должна быть хотя бы одна экскурсия"
    # У каждой экскурсии есть маршрут, у каждого занятия — экскурсия и гид.
    assert all(item.route.id in route_ids for item in data["excursions"])
    assert all(item.excursion.id in excursion_ids for item in data["schedules"])
    assert all(item.guide.id in guide_ids for item in data["schedules"])
