"""Контекстный процессор: общие данные для всех шаблонов.

Счётчики нужны в подвале каждой страницы, поэтому их удобно считать
один раз в процессоре, а не передавать из каждой view-функции.
"""

from datetime import date


def counters(request):
    """Количество объектов проекта и текущая дата."""
    from excursions.models import Excursion
    from guides.models import Guide
    from routes.models import Route
    from schedules.models import Schedule

    return {
        "site_counters": {
            "guides": Guide.objects.count(),
            "routes": Route.objects.count(),
            "excursions": Excursion.objects.count(),
            "schedules": Schedule.objects.count(),
        },
        "today": date.today(),
    }
