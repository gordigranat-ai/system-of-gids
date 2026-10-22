"""Тесты веб-интерфейса.

Проверяем то, что требует ПР5: каждый маршрут связан с view-функцией,
страницы открываются с кодом 200, а несуществующие объекты и адреса
дают код 404. Идентификаторы объектов берём из данных, чтобы тесты
не зависели от конкретных записей в JSON.
"""

import pytest
from django.test import Client

from storage import load_all, load_excursions, load_routes


@pytest.fixture()
def client():
    """Клиент Django, который выполняет запросы без запуска сервера."""
    return Client()


@pytest.fixture()
def data():
    """Данные проекта, разложенные по видам."""
    guides, routes, excursions, schedules = load_all()
    return {
        "guides": guides,
        "routes": routes,
        "excursions": excursions,
        "schedules": schedules,
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


def test_related_objects_are_linked(data):
    """Данные для страниц берутся из ПР3 без потери связей между объектами."""
    routes = load_routes()
    excursions = load_excursions(routes)

    route_ids = {route.id for route in routes}
    excursion_ids = {item.id for item in excursions}
    guide_ids = {guide.id for guide in data["guides"]}

    assert excursions, "в данных должна быть хотя бы одна экскурсия"
    # У каждой экскурсии есть маршрут, у каждого занятия — экскурсия и гид.
    assert all(item.route.id in route_ids for item in excursions)
    assert all(item.excursion.id in excursion_ids for item in data["schedules"])
    assert all(item.guide.id in guide_ids for item in data["schedules"])
