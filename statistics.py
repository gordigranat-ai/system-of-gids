"""Статистика по проекту.

Считаем то, что интересно руководителю: сколько занятий у гидов, какие
маршруты популярнее, сколько денег принесли экскурсии, как заполняются
занятия. Функции только читают данные, ничего не меняют.
"""

from models import STATUS_CANCELLED, STATUS_DONE
from utils import pluralize, weekday_title


def count_schedules_by_guide(schedules, guides):
    """Сколько занятий у каждого гида. Отменённые не считаем."""
    rows = []
    for guide in guides:
        count = 0
        for item in schedules:
            if item.guide.id == guide.id and not item.is_cancelled:
                count += 1
        if count > 0:
            rows.append((guide.name, count))
    return sorted(rows, key=lambda row: row[1], reverse=True)


def count_schedules_by_route(schedules, routes):
    """Сколько занятий пришлось на каждый маршрут."""
    rows = []
    for route in routes:
        count = 0
        for item in schedules:
            if item.route.id == route.id:
                count += 1
        if count > 0:
            rows.append((route.name, count))
    return sorted(rows, key=lambda row: row[1], reverse=True)


def total_revenue(schedules):
    """Общая выручка по занятиям, кроме отменённых."""
    total = 0
    for item in schedules:
        if not item.is_cancelled:
            total += item.revenue
    return round(total, 2)


def occupancy_report(schedules):
    """Заполняемость занятий: дата, мест, занято, свободно."""
    rows = []
    for item in schedules:
        if not item.is_cancelled:
            rows.append((item.date + " " + item.start_time,
                         item.excursion.max_participants, item.booked, item.free_seats))
    return sorted(rows, key=lambda row: row[0])


def weekday_activity(schedules):
    """Сколько занятий приходится на каждый день недели."""
    counters = {}
    for item in schedules:
        if item.is_cancelled:
            continue
        title = weekday_title(item.schedule_date)
        counters[title] = counters.get(title, 0) + 1
    return sorted(counters.items(), key=lambda row: row[1], reverse=True)


def build_summary(schedules):
    """Сводные показатели одним словарём."""
    active = [item for item in schedules if not item.is_cancelled]
    done = [item for item in schedules if item.status == STATUS_DONE]
    cancelled = [item for item in schedules if item.status == STATUS_CANCELLED]

    participants = 0
    for item in active:
        participants += item.booked

    return {
        "total": len(schedules),
        "done": len(done),
        "cancelled": len(cancelled),
        "participants": participants,
        "revenue": total_revenue(schedules),
    }


def summary_line(summary):
    """Сводные показатели одной строкой."""
    word = pluralize(summary["participants"], ("участник", "участника", "участников"))
    return (f"Занятий: {summary['total']} (проведено {summary['done']}, "
            f"отменено {summary['cancelled']}); участников: {summary['participants']} "
            f"{word}; выручка: {summary['revenue']:.2f} руб.")
