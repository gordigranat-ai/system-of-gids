"""Тесты страниц проекта: маршруты, фильтры, сортировка, пагинация, 404."""

from datetime import date, time

import pytest

from schedules.models import Schedule

pytestmark = pytest.mark.django_db


def test_home_page(client):
    """Главная страница открывается и содержит название проекта."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Сервис управления гидами" in response.content.decode()


def test_guides_list(client, dataset):
    """Список гидов показывает данные из базы."""
    response = client.get("/guides/")
    assert response.status_code == 200
    assert "Анна Смирнова" in response.content.decode()


def test_guides_search(client, dataset):
    """Поиск по имени отбирает записи."""
    found = client.get("/guides/", {"q": "Анна"})
    empty = client.get("/guides/", {"q": "Петров"})

    assert "Анна Смирнова" in found.content.decode()
    assert "Анна Смирнова" not in empty.content.decode()


def test_guides_filter_by_language(client, dataset):
    """Фильтр по языку использует поле languages."""
    response = client.get("/guides/", {"language": "английский"})
    assert list(response.context["guides"]) == [dataset["guide"]]

    missing = client.get("/guides/", {"language": "французский"})
    assert list(missing.context["guides"]) == []


def test_guides_sort_by_rating(client, guide):
    """Сортировка по рейтингу передаётся в order_by()."""
    response = client.get("/guides/", {"sort": "rating"})
    assert response.status_code == 200
    assert response.context["guides"].query.order_by == ("-rating",)


def test_guide_detail(client, dataset):
    """Карточка гида открывается и показывает занятия."""
    guide = dataset["guide"]
    response = client.get(f"/guides/{guide.pk}/")
    assert response.status_code == 200
    html = response.content.decode()
    assert "Анна Смирнова" in html
    assert "Знакомство с городом" in html


def test_guide_detail_404(client):
    """Несуществующий гид даёт 404 и свою страницу."""
    response = client.get("/guides/9999/")
    assert response.status_code == 404
    assert "Гид не найден" in response.content.decode()


def test_available_guides_excludes_busy(client, dataset):
    """Занятый в этот день гид в список свободных не попадает."""
    guide = dataset["guide"]
    busy = client.get("/guides/available/", {"date": "2026-03-10"})
    free = client.get("/guides/available/", {"date": "2026-03-11"})

    assert guide not in list(busy.context["guides"])
    assert guide in list(free.context["guides"])


def test_available_guides_ignores_cancelled(client, dataset):
    """Отменённое занятие время гида не занимает."""
    guide = dataset["guide"]
    Schedule.objects.create(
        excursion=dataset["excursion"],
        guide=guide,
        date=date(2026, 3, 12),
        start_time=time(9, 0),
        status="cancelled",
    )
    response = client.get("/guides/available/", {"date": "2026-03-12"})
    assert guide in list(response.context["guides"])


def test_available_guides_bad_date(client):
    """Некорректная дата не ломает страницу, а даёт сообщение."""
    response = client.get("/guides/available/", {"date": "2026-13-45"})
    assert response.status_code == 200
    assert "формате ГГГГ-ММ-ДД" in response.content.decode()


def test_routes_list_and_filter(client, dataset):
    """Список маршрутов и фильтр по сложности."""
    all_routes = client.get("/routes/")
    assert all_routes.status_code == 200
    assert "Исторический центр" in all_routes.content.decode()

    empty = client.get("/routes/", {"difficulty": "сложный"})
    assert list(empty.context["routes"]) == []


def test_route_detail_and_404(client, dataset):
    """Карточка маршрута открывается, несуществующий маршрут — 404."""
    route = dataset["route"]
    response = client.get(f"/routes/{route.slug}/")
    assert response.status_code == 200
    assert "Исторический центр" in response.content.decode()

    assert client.get("/routes/9999/").status_code == 404


def test_excursions_filter_by_price(client, dataset):
    """Фильтр по максимальной цене работает на уровне базы."""
    fits = client.get("/excursions/", {"max_price": "2000"})
    no_fit = client.get("/excursions/", {"max_price": "100"})

    assert dataset["excursion"] in list(fits.context["excursions"])
    assert list(no_fit.context["excursions"]) == []


def test_excursions_bad_price(client, dataset):
    """Некорректная цена показывает предупреждение, а не ошибку 500."""
    response = client.get("/excursions/", {"max_price": "дорого"})
    assert response.status_code == 200
    assert "Цена должна быть числом" in response.content.decode()


def test_excursion_detail(client, dataset):
    """Карточка экскурсии показывает стоимость группы из четырёх человек."""
    excursion = dataset["excursion"]
    response = client.get(f"/excursions/{excursion.pk}/")
    assert response.status_code == 200
    assert "7 200" in response.content.decode() or "7200" in response.content.decode()


def test_schedules_list_and_detail(client, dataset):
    """Список занятий и карточка занятия открываются."""
    assert client.get("/schedules/").status_code == 200

    schedule = dataset["schedule"]
    response = client.get(f"/schedules/{schedule.pk}/")
    assert response.status_code == 200
    assert "Знакомство с городом" in response.content.decode()


def test_schedules_pagination(client, many_schedules):
    """Семь занятий делятся на две страницы по пять."""
    first = client.get("/schedules/")
    second = client.get("/schedules/", {"page": 2})

    assert first.context["page_obj"].paginator.num_pages == 2
    assert len(first.context["schedules"]) == 5
    assert len(second.context["schedules"]) == 2


def test_schedules_status_filter(client, many_schedules):
    """Фильтр по статусу оставляет только нужные занятия."""
    response = client.get("/schedules/", {"status": "completed"})
    assert all(
        item.status == "completed" for item in response.context["schedules"]
    )


def test_schedules_date_range(client, many_schedules):
    """Фильтр по периоду сравнивает даты."""
    response = client.get(
        "/schedules/",
        {"date_from": "2026-03-02", "date_to": "2026-03-04"},
    )
    dates = [item.date for item in response.context["schedules"]]
    assert dates == [date(2026, 3, 2), date(2026, 3, 3), date(2026, 3, 4)]


def test_schedules_sort_by_booked(client, many_schedules):
    """Сортировка по числу броней ставит первым самое загруженное занятие."""
    response = client.get("/schedules/", {"sort": "booked"})
    first = list(response.context["schedules"])[0]
    assert first.booked == 7


def test_schedules_bad_guide(client, many_schedules):
    """Некорректный параметр гида не ломает страницу: форма показывает ошибку."""
    response = client.get("/schedules/", {"guide": "abc"})
    form = response.context["form"]

    assert response.status_code == 200
    assert form.is_valid() is False
    assert form.errors


def test_active_schedules_excludes_cancelled(client, dataset):
    """Страница активных занятий не показывает отменённые."""
    Schedule.objects.create(
        excursion=dataset["excursion"],
        guide=dataset["guide"],
        date=date(2026, 7, 1),
        start_time=time(10, 0),
        status="cancelled",
    )
    response = client.get("/schedules/active/")
    statuses = [item.status for item in response.context["schedules"]]
    assert "cancelled" not in statuses


def test_statistics_totals(client, dataset):
    """Статистика считает агрегаты через aggregate() и annotate()."""
    response = client.get("/schedules/statistics/")
    totals = response.context["totals"]

    assert totals["schedules"] == 1
    assert totals["active"] == 1
    assert totals["booked_total"] == 8
    assert totals["revenue"] == 14400

    excursion_row = list(response.context["by_excursion"])[0]
    assert excursion_row.schedules_count == 1
    assert excursion_row.booked_total == 8


def test_unknown_address_returns_404(client):
    """Адрес без маршрута обрабатывается страницей 404."""
    response = client.get("/nonexistent/")
    assert response.status_code == 404


def test_navigation_links(client):
    """В меню есть ссылки на все разделы проекта."""
    html = client.get("/").content.decode()
    for url in ("/guides/", "/routes/", "/excursions/", "/schedules/"):
        assert f'href="{url}"' in html
