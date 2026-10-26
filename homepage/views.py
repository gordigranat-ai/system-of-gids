"""Главная страница и обработчик 404.

Счётчики для главной считает один SQL-запрос.
"""

from django.shortcuts import render

from db.database import fetch_one

COUNTERS_SQL = """
    SELECT
        (SELECT COUNT(*) FROM guides) AS guides,
        (SELECT COUNT(*) FROM routes) AS routes,
        (SELECT COUNT(*) FROM excursions) AS excursions,
        (SELECT COUNT(*) FROM schedules) AS schedules;
"""


def index(request):
    """Главная страница проекта."""
    context = {"counters": fetch_one(COUNTERS_SQL)}
    return render(request, "homepage/index.html", context)


def page_not_found(request, exception):
    """Собственная страница 404 для адресов, которым не нашлось маршрута."""
    return render(request, "homepage/page_not_found.html", status=404)
