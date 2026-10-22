"""Страницы гидов: список и карточка отдельного гида.

Данные берутся средствами ПР3: storage.load_guides() возвращает объекты
Guide, а правила предметной области (языки, статус) живут в самих классах.
"""

from django.http import HttpResponse

from homepage.views import page
from models import NotFoundError, get_guide
from storage import load_guides, load_schedules, load_routes, load_excursions


def guides(request):
    """Список гидов с языками и статусом работы."""
    guides_list = load_guides()

    items = ""
    for guide in guides_list:
        languages = ", ".join(guide.languages)
        status = "работает" if guide.is_active else "не работает"
        badge = "bg-success" if guide.is_active else "bg-secondary"
        items += f"""
        <li class="list-group-item d-flex justify-content-between align-items-center">
            <span>
                <a href="/guides/{guide.id}/">{guide.name}</a>
                <small class="text-muted">{guide.specialization}</small>
            </span>
            <span class="text-muted">языки: {languages}</span>
            <span class="badge {badge}">{status}</span>
        </li>
        """

    if not items:
        items = '<li class="list-group-item">Гидов пока нет.</li>'

    content = f"""
    <h1>Гиды</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Гиды – экскурсионное бюро", content))


def guide_detail(request, guide_id):
    """Карточка гида и его занятия в расписании."""
    guides_list = load_guides()

    try:
        guide = get_guide(guides_list, guide_id)
    except NotFoundError:
        content = """
        <h1 class="text-danger">Гид не найден</h1>
        <a href="/guides/" class="btn btn-outline-secondary">
            ← к списку гидов
        </a>
        """
        return HttpResponse(page("Гид не найден", content), status=404)

    routes_list = load_routes()
    excursions_list = load_excursions(routes_list)
    schedules_list = load_schedules(excursions_list, guides_list)

    own_schedules = [item for item in schedules_list if item.guide.id == guide.id]

    items = ""
    for item in own_schedules:
        items += f"""
        <li class="list-group-item">
            <a href="/schedules/{item.id}/">{item.date} в {item.start_time}</a>
            – {item.excursion.title}
        </li>
        """
    if not items:
        items = '<li class="list-group-item">Занятий пока нет.</li>'

    status = "работает" if guide.is_active else "не работает"
    badge = "bg-success" if guide.is_active else "bg-secondary"
    languages = ", ".join(guide.languages)

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{guide.name}</h5>
            <p class="card-text"><strong>Специализация:</strong> {guide.specialization}</p>
            <p class="card-text"><strong>Языки:</strong> {languages}</p>
            <p class="card-text"><strong>Стаж:</strong> {guide.experience_years} лет</p>
            <p class="card-text"><strong>Рейтинг:</strong> {guide.rating}</p>
            <p class="card-text">
                Статус: <span class="badge {badge}">{status}</span>
            </p>
            <a href="/guides/" class="btn btn-outline-secondary">
                ← к списку гидов
            </a>
        </div>
    </div>
    <h2 class="mt-4">Занятия гида</h2>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page(guide.name, content))
