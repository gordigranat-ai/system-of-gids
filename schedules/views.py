"""Страницы расписания: список занятий, активные занятия и статистика.

Списки и карточки собираются из объектов (db.repository), а страница
статистики показывает результат SQL-запросов напрямую: строки sqlite3.Row
передаются в шаблон через контекст, поля читаются по именам.
"""

from django.shortcuts import render

from db.database import fetch_all, fetch_one
from db.repository import get_schedule, list_schedules

STATISTICS_BY_GUIDE = """
    SELECT
        g.name AS guide_name,
        COUNT(s.id) AS schedules_count,
        COALESCE(SUM(s.booked), 0) AS booked_total
    FROM guides AS g
    LEFT JOIN schedules AS s
           ON s.guide_id = g.id
          AND s.status <> 'отменена'
    GROUP BY g.id, g.name
    ORDER BY schedules_count DESC, g.name;
"""

STATISTICS_BY_EXCURSION = """
    SELECT
        e.title,
        COUNT(s.id) AS schedules_count,
        COALESCE(SUM(s.booked), 0) AS booked_total,
        COALESCE(SUM(s.booked * e.base_price), 0) AS revenue,
        ROUND(
            AVG(CAST(s.booked AS REAL) / e.max_participants) * 100,
            1
        ) AS load_percent
    FROM excursions AS e
    LEFT JOIN schedules AS s
           ON s.excursion_id = e.id
          AND s.status <> 'отменена'
    GROUP BY e.id, e.title
    ORDER BY revenue DESC;
"""

STATISTICS_SUMMARY = """
    SELECT
        (SELECT COUNT(*) FROM guides) AS guides,
        (SELECT COUNT(*) FROM routes) AS routes,
        (SELECT COUNT(*) FROM excursions) AS excursions,
        (SELECT COUNT(*) FROM schedules) AS schedules,
        (SELECT COUNT(*) FROM schedules WHERE status <> 'отменена')
            AS active_schedules;
"""


def schedules(request):
    """Все занятия расписания с датой, гидом и загрузкой."""
    context = {"schedules": list_schedules()}
    return render(request, "schedules/schedule_list.html", context)


def active_schedules(request):
    """Занятия, которые не отменены: их ещё предстоит провести."""
    context = {"schedules": list_schedules(only_active=True)}
    return render(request, "schedules/active.html", context)


def statistics(request):
    """Статистика по гидам и экскурсиям: результат SQL-запросов."""
    context = {
        "summary": fetch_one(STATISTICS_SUMMARY),
        "by_guide": fetch_all(STATISTICS_BY_GUIDE),
        "by_excursion": fetch_all(STATISTICS_BY_EXCURSION),
    }
    return render(request, "schedules/statistics.html", context)


def schedule_detail(request, schedule_id):
    """Карточка занятия: участники, свободные места, выручка и статус."""
    schedule = get_schedule(schedule_id)

    if schedule is None:
        context = {
            "message": "Занятие не найдено",
            "hint": "Занятия с таким идентификатором нет в расписании.",
            "list_url": "schedules:list",
        }
        return render(request, "not_found.html", context, status=404)

    context = {"schedule": schedule}
    return render(request, "schedules/schedule_detail.html", context)
