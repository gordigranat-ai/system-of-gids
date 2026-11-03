"""Тесты административной панели: доступ, поиск, действия, встроенные формы."""

import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


@pytest.fixture()
def admin_user(db):
    """Суперпользователь для входа в админку."""
    return get_user_model().objects.create_superuser(
        username="admin_test",
        email="admin_test@example.com",
        password="test12345",
    )


@pytest.fixture()
def admin_client(client, admin_user):
    """Клиент, вошедший в административную панель."""
    client.force_login(admin_user)
    return client


def test_admin_requires_login(client):
    """Без входа админка перенаправляет на форму логина."""
    response = client.get("/admin/")
    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


def test_admin_index_opens(admin_client):
    """Главная страница админки открывается."""
    response = admin_client.get("/admin/")
    assert response.status_code == 200
    assert "Экскурсионное бюро" in response.content.decode()


def test_schedule_changelist_and_search(admin_client, dataset):
    """Список занятий открывается, поиск по гиду отбирает записи."""
    response = admin_client.get("/admin/schedules/schedule/", {"q": "Анна"})
    assert response.status_code == 200
    assert dataset["guide"].name in response.content.decode()


def test_admin_action_cancels_schedule(admin_client, dataset):
    """Массовое действие переводит занятие в статус «отменена»."""
    schedule = dataset["schedule"]
    response = admin_client.post(
        "/admin/schedules/schedule/",
        {
            "action": "mark_cancelled",
            "_selected_action": [str(schedule.pk)],
            "index": "0",
        },
        follow=True,
    )
    assert response.status_code == 200

    schedule.refresh_from_db()
    assert schedule.status == "cancelled"


def test_guide_change_page_has_inline(admin_client, dataset):
    """На странице гида видна встроенная форма его занятий."""
    guide = dataset["guide"]
    response = admin_client.get(f"/admin/guides/guide/{guide.pk}/change/")
    html = response.content.decode()

    assert response.status_code == 200
    assert "Расписание" in html
    assert dataset["excursion"].title in html
