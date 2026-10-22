"""Страницы экскурсий: список и карточка экскурсии.

Стоимость и скидки считают методы класса Excursion: в веб-слое логика
предметной области не повторяется.
"""

from django.http import HttpResponse

from homepage.views import page
from models import NotFoundError, get_excursion
from storage import load_excursions, load_routes


def excursions(request):
    """Список экскурсий с ценой и числом мест."""
    routes_list = load_routes()
    excursions_list = load_excursions(routes_list)

    items = ""
    for excursion in excursions_list:
        items += f"""
        <li class="list-group-item">
            <a href="/excursions/{excursion.id}/">{excursion.title}</a>
            <small class="text-muted">
                {excursion.kind} · {excursion.base_price} ₽ · до
                {excursion.max_participants} человек
            </small>
            <div><small class="text-muted">маршрут: {excursion.route.name}</small></div>
        </li>
        """

    if not items:
        items = '<li class="list-group-item">Экскурсий пока нет.</li>'

    content = f"""
    <h1>Экскурсии</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Экскурсии – экскурсионное бюро", content))


def excursion_detail(request, excursion_id):
    """Карточка экскурсии: маршрут, цена, вместимость и пример стоимости."""
    routes_list = load_routes()
    excursions_list = load_excursions(routes_list)

    try:
        excursion = get_excursion(excursions_list, excursion_id)
    except NotFoundError:
        content = """
        <h1 class="text-danger">Экскурсия не найдена</h1>
        <a href="/excursions/" class="btn btn-outline-secondary">
            ← к списку экскурсий
        </a>
        """
        return HttpResponse(page("Экскурсия не найдена", content), status=404)

    languages = ", ".join(excursion.languages)

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{excursion.title}</h5>
            <p class="card-text"><strong>Вид:</strong> {excursion.kind}</p>
            <p class="card-text">
                <strong>Маршрут:</strong>
                <a href="/routes/{excursion.route.id}/">{excursion.route.name}</a>
                ({excursion.duration_hours} ч, {excursion.route.difficulty})
            </p>
            <p class="card-text">
                <strong>Цена за человека:</strong> {excursion.base_price} ₽
            </p>
            <p class="card-text">
                <strong>Максимум участников:</strong> {excursion.max_participants}
            </p>
            <p class="card-text"><strong>Минимальный возраст:</strong> {excursion.min_age}</p>
            <p class="card-text"><strong>Языки:</strong> {languages}</p>
            <a href="/excursions/" class="btn btn-outline-secondary">
                ← к списку экскурсий
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(excursion.title, content))
