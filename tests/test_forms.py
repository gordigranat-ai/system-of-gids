"""Тесты форм расписания и гидов: валидация, создание, правка, отмена."""

from datetime import time, timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.utils import timezone

from guides.forms import GuideForm
from schedules.forms import ScheduleFilterForm, ScheduleForm
from schedules.models import Schedule, ScheduleStatus

pytestmark = pytest.mark.django_db

# Картинка 1x1 пиксель — настоящий PNG, чтобы сработала проверка ImageField.
TINY_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00"
    b"\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB\x60\x82"
)


def future_day(days=7):
    """Дата в будущем — форма занятий не принимает прошедшие даты."""
    return timezone.localdate() + timedelta(days=days)


def make_busy_schedule(excursion, guide, day):
    """Существующее занятие гида на 10:00, чтобы проверить занятость."""
    return Schedule.objects.create(
        excursion=excursion,
        guide=guide,
        date=day,
        start_time=time(10, 0),
        booked=1,
        status=ScheduleStatus.ACTIVE,
    )


# --- форма фильтрации ---------------------------------------------------

def test_filter_form_valid_and_applied(dataset):
    """Проверенная форма фильтрует набор занятий."""
    form = ScheduleFilterForm({"status": "active", "sort": "booked"})
    assert form.is_valid()

    queryset = form.filter_queryset(Schedule.objects.all())
    assert list(queryset) == [dataset["schedule"]]


def test_filter_form_checks_period():
    """Дата начала позже даты окончания — ошибка формы, а не исключение."""
    form = ScheduleFilterForm({
        "date_from": "2026-03-15",
        "date_to": "2026-03-10",
    })
    assert not form.is_valid()
    assert "Дата начала не может быть позже" in str(form.non_field_errors())


def test_filter_form_rejects_bad_date():
    """Некорректная дата — ошибка поля, страница не падает."""
    form = ScheduleFilterForm({"date_from": "2026-13-45"})
    assert not form.is_valid()
    assert "date_from" in form.errors


# --- форма занятия ------------------------------------------------------

def test_schedule_form_rejects_past_date(excursion, guide):
    """Дата в прошлом не принимается."""
    form = ScheduleForm({
        "excursion": excursion.pk,
        "guide": guide.pk,
        "date": timezone.localdate() - timedelta(days=1),
        "start_time": "10:00",
        "booked": 1,
    })
    assert not form.is_valid()
    assert "прошедшую дату" in str(form.errors["date"])


def test_schedule_form_rejects_busy_guide(dataset):
    """Гид не может вести два занятия в одно время."""
    day = future_day()
    make_busy_schedule(dataset["excursion"], dataset["guide"], day)

    form = ScheduleForm({
        "excursion": dataset["excursion"].pk,
        "guide": dataset["guide"].pk,
        "date": day,
        "start_time": "10:30",
        "booked": 2,
    })
    assert not form.is_valid()
    assert "Гид занят" in str(form.non_field_errors())


def test_schedule_form_edit_excludes_itself(dataset):
    """При редактировании занятие не конфликтует само с собой."""
    day = future_day()
    schedule = make_busy_schedule(
        dataset["excursion"], dataset["guide"], day,
    )

    form = ScheduleForm(
        {
            "excursion": dataset["excursion"].pk,
            "guide": dataset["guide"].pk,
            "date": day,
            "start_time": "10:00",
            "booked": 3,
        },
        instance=schedule,
    )
    assert form.is_valid(), form.errors


def test_schedule_form_rejects_too_many_seats(dataset):
    """Броней не может быть больше, чем мест на экскурсии."""
    form = ScheduleForm({
        "excursion": dataset["excursion"].pk,
        "guide": dataset["guide"].pk,
        "date": future_day(),
        "start_time": "12:00",
        "booked": 100,
    })
    assert not form.is_valid()
    assert "booked" in form.errors


def test_cancelled_schedule_does_not_block_guide(dataset):
    """Отменённое занятие время гида не занимает."""
    day = future_day()
    busy = make_busy_schedule(dataset["excursion"], dataset["guide"], day)
    busy.cancel()

    form = ScheduleForm({
        "excursion": dataset["excursion"].pk,
        "guide": dataset["guide"].pk,
        "date": day,
        "start_time": "10:30",
        "booked": 1,
    })
    assert form.is_valid(), form.errors


# --- страницы с формами -------------------------------------------------

def test_create_page_opens(client, dataset):
    """Форма создания занятия открывается и содержит поля."""
    response = client.get("/schedules/new/")
    html = response.content.decode()

    assert response.status_code == 200
    assert "Новое занятие" in html
    assert 'name="date"' in html
    assert "csrfmiddlewaretoken" in html


def test_create_schedule_by_post(client, dataset):
    """POST с корректными данными создаёт занятие и перенаправляет."""
    day = future_day()
    response = client.post(
        "/schedules/new/",
        {
            "excursion": dataset["excursion"].pk,
            "guide": dataset["guide"].pk,
            "date": day.isoformat(),
            "start_time": "15:00",
            "booked": 4,
            "note": "Новая группа",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert "добавлено в расписание" in response.content.decode()

    created = Schedule.objects.get(date=day, start_time=time(15, 0))
    assert created.booked == 4
    assert created.status == ScheduleStatus.ACTIVE


def test_create_schedule_shows_errors(client, dataset):
    """Ошибки формы возвращаются на страницу, а не в исключение."""
    response = client.post(
        "/schedules/new/",
        {
            "excursion": dataset["excursion"].pk,
            "guide": dataset["guide"].pk,
            "date": (timezone.localdate() - timedelta(days=3)).isoformat(),
            "start_time": "15:00",
            "booked": 1,
        },
    )
    html = response.content.decode()

    assert response.status_code == 200
    assert "прошедшую дату" in html
    assert Schedule.objects.count() == 1


def test_edit_schedule_by_post(client, dataset):
    """Редактирование меняет данные существующего занятия."""
    schedule = dataset["schedule"]
    response = client.post(
        f"/schedules/{schedule.pk}/edit/",
        {
            "excursion": dataset["excursion"].pk,
            "guide": dataset["guide"].pk,
            "date": future_day().isoformat(),
            "start_time": "11:00",
            "booked": 5,
            "note": "Перенесли",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert "Изменения сохранены" in response.content.decode()

    schedule.refresh_from_db()
    assert schedule.booked == 5
    assert schedule.note == "Перенесли"


def test_cancel_view_requires_confirmation(client, dataset):
    """GET показывает подтверждение, статус ещё не меняется."""
    schedule = dataset["schedule"]
    response = client.get(f"/schedules/{schedule.pk}/cancel/")

    assert response.status_code == 200
    assert "Отменить занятие" in response.content.decode()

    schedule.refresh_from_db()
    assert schedule.status == ScheduleStatus.ACTIVE


def test_cancel_schedule_by_post(client, dataset):
    """POST отменяет занятие, не удаляя его из базы."""
    schedule = dataset["schedule"]
    response = client.post(
        f"/schedules/{schedule.pk}/cancel/",
        follow=True,
    )
    assert response.status_code == 200
    assert "Занятие отменено" in response.content.decode()

    schedule.refresh_from_db()
    assert schedule.status == ScheduleStatus.CANCELLED
    assert Schedule.objects.count() == 1


def test_missing_schedule_forms_return_404(client):
    """Несуществующее занятие — страница 404."""
    assert client.get("/schedules/9999/edit/").status_code == 404
    assert client.get("/schedules/9999/cancel/").status_code == 404


def test_post_requires_csrf_token(dataset):
    """POST без CSRF-токена отклоняется."""
    strict_client = Client(enforce_csrf_checks=True, SERVER_NAME="127.0.0.1")
    response = strict_client.post(
        "/schedules/new/",
        {
            "excursion": dataset["excursion"].pk,
            "guide": dataset["guide"].pk,
            "date": future_day().isoformat(),
            "start_time": "16:00",
            "booked": 1,
        },
    )
    assert response.status_code == 403


def test_post_with_csrf_token_works(dataset):
    """С токеном из формы POST проходит."""
    strict_client = Client(enforce_csrf_checks=True, SERVER_NAME="127.0.0.1")
    page = strict_client.get("/schedules/new/")
    token = page.context["csrf_token"]

    response = strict_client.post(
        "/schedules/new/",
        {
            "csrfmiddlewaretoken": str(token),
            "excursion": dataset["excursion"].pk,
            "guide": dataset["guide"].pk,
            "date": future_day().isoformat(),
            "start_time": "16:00",
            "booked": 1,
        },
    )
    assert response.status_code == 302


# --- форма гида и фотография -------------------------------------------

def test_guide_form_rejects_big_photo(guide, monkeypatch, settings, tmp_path):
    """Слишком большой файл не принимается: проверяется размер картинки."""
    import guides.forms as guide_forms

    # Ограничение уменьшено, чтобы не готовить файл на два мегабайта.
    monkeypatch.setattr(guide_forms, "MAX_PHOTO_SIZE", 10)

    photo = SimpleUploadedFile("guide.png", TINY_PNG, content_type="image/png")
    form = GuideForm(
        {
            "name": guide.name,
            "specialization": guide.specialization,
            "languages": guide.languages,
            "experience_years": guide.experience_years,
            "rating": guide.rating,
            "is_active": True,
        },
        {"photo": photo},
        instance=guide,
    )
    assert not form.is_valid()
    assert "Загрузите изображение поменьше" in str(form.errors["photo"])


def test_guide_photo_upload(client, guide, settings, tmp_path):
    """Фотография сохраняется и выводится на странице гида."""
    settings.MEDIA_ROOT = tmp_path

    photo = SimpleUploadedFile(
        "guide.png", TINY_PNG, content_type="image/png",
    )

    response = client.post(
        f"/guides/{guide.pk}/edit/",
        {
            "name": guide.name,
            "specialization": guide.specialization,
            "languages": guide.languages,
            "experience_years": guide.experience_years,
            "rating": guide.rating,
            "is_active": True,
            "photo": photo,
        },
        follow=True,
    )
    assert response.status_code == 200

    guide.refresh_from_db()
    assert guide.photo
    assert f"/media/{guide.photo.name}" in response.content.decode()
