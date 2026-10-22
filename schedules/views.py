"""Страницы расписания: список занятий и карточка занятия.

Занятие связывает экскурсию и гида, поэтому на страницах выводятся
связанные объекты: schedule.excursion и schedule.guide.
"""

from django.http import HttpResponse

from homepage.views import page
from models import NotFoundError, get_schedule
from storage import load_all

STATUS_CLASSES = {
    "запланирована": "bg-success",
    "проведена": "bg-secondary",
    "отменена": "bg-danger",
}


def schedules(request):
    """Список занятий расписания с датой, гидом и загрузкой."""
    _, _, _, schedules_list = load_all()

    items = ""
    for item in schedules_list:
        badge = STATUS_CLASSES.get(item.status, "bg-light")
        items += f"""
        <li class="list-group-item d-flex justify-content-between align-items-center">
            <span>
                <a href="/schedules/{item.id}/">{item.date} в {item.start_time}</a>
                – {item.excursion.title}
                <small class="text-muted">гид: {item.guide.name}</small>
            </span>
            <span class="text-muted">
                {item.booked} из {item.excursion.max_participants} мест
            </span>
            <span class="badge {badge}">{item.status}</span>
        </li>
        """

    if not items:
        items = '<li class="list-group-item">Занятий пока нет.</li>'

    content = f"""
    <h1>Расписание</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Расписание – экскурсионное бюро", content))


def schedule_detail(request, schedule_id):
    """Карточка занятия: участники, свободные места, выручка и статус."""
    _, _, _, schedules_list = load_all()

    try:
        item = get_schedule(schedules_list, schedule_id)
    except NotFoundError:
        content = """
        <h1 class="text-danger">Занятие не найдено</h1>
        <a href="/schedules/" class="btn btn-outline-secondary">
            ← к расписанию
        </a>
        """
        return HttpResponse(page("Занятие не найдено", content), status=404)

    badge = STATUS_CLASSES.get(item.status, "bg-light")
    note = item.note or "без примечания"

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{item.excursion.title}</h5>
            <p class="card-text"><strong>Дата:</strong> {item.date}</p>
            <p class="card-text"><strong>Начало:</strong> {item.start_time}</p>
            <p class="card-text">
                <strong>Гид:</strong>
                <a href="/guides/{item.guide.id}/">{item.guide.name}</a>
            </p>
            <p class="card-text">
                <strong>Маршрут:</strong> {item.route.name}
                ({item.excursion.duration_hours} ч)
            </p>
            <p class="card-text">
                <strong>Забронировано:</strong> {item.booked} из
                {item.excursion.max_participants} мест
            </p>
            <p class="card-text"><strong>Свободно мест:</strong> {item.free_seats}</p>
            <p class="card-text"><strong>Выручка:</strong> {item.revenue} ₽</p>
            <p class="card-text">
                Статус: <span class="badge {badge}">{item.status}</span>
            </p>
            <p class="card-text"><strong>Примечание:</strong> {note}</p>
            <a href="/schedules/" class="btn btn-outline-secondary">
                ← к расписанию
            </a>
        </div>
    </div>
    """
    return HttpResponse(page("Занятие " + item.date, content))
