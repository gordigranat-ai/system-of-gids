"""Страницы маршрутов: список и карточка маршрута."""

from django.http import HttpResponse

from homepage.views import page
from models import NotFoundError, get_route
from storage import load_excursions, load_routes


def routes(request):
    """Список маршрутов с продолжительностью и сложностью."""
    routes_list = load_routes()

    items = ""
    for route in routes_list:
        languages = ", ".join(route.required_languages)
        items += f"""
        <li class="list-group-item">
            <a href="/routes/{route.id}/">{route.name}</a>
            <small class="text-muted">
                {route.duration_hours} ч · {route.difficulty} · {route.distance_km} км
            </small>
            <div><small class="text-muted">языки: {languages}</small></div>
        </li>
        """

    if not items:
        items = '<li class="list-group-item">Маршрутов пока нет.</li>'

    content = f"""
    <h1>Маршруты</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Маршруты – экскурсионное бюро", content))


def route_detail(request, route_id):
    """Карточка маршрута и экскурсии, которые по нему проводятся."""
    routes_list = load_routes()

    try:
        route = get_route(routes_list, route_id)
    except NotFoundError:
        content = """
        <h1 class="text-danger">Маршрут не найден</h1>
        <a href="/routes/" class="btn btn-outline-secondary">
            ← к списку маршрутов
        </a>
        """
        return HttpResponse(page("Маршрут не найден", content), status=404)

    excursions_list = load_excursions(routes_list)
    own_excursions = [item for item in excursions_list if item.route.id == route.id]

    items = ""
    for excursion in own_excursions:
        items += f"""
        <li class="list-group-item">
            <a href="/excursions/{excursion.id}/">{excursion.title}</a>
            – {excursion.base_price} ₽ за человека
        </li>
        """
    if not items:
        items = '<li class="list-group-item">Экскурсий по этому маршруту нет.</li>'

    languages = ", ".join(route.required_languages)

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{route.name}</h5>
            <p class="card-text">{route.description}</p>
            <p class="card-text">
                <strong>Продолжительность:</strong> {route.duration_hours} ч
            </p>
            <p class="card-text">
                <strong>Протяжённость:</strong> {route.distance_km} км
            </p>
            <p class="card-text"><strong>Сложность:</strong> {route.difficulty}</p>
            <p class="card-text"><strong>Языки:</strong> {languages}</p>
            <a href="/routes/" class="btn btn-outline-secondary">
                ← к списку маршрутов
            </a>
        </div>
    </div>
    <h2 class="mt-4">Экскурсии на маршруте</h2>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page(route.name, content))
