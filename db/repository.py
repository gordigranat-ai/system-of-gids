"""Выборка объектов предметной области из базы SQLite.

Шаблоны страниц работают с объектами классов Guide, Route, Excursion
и Schedule, поэтому строки базы превращаются в объекты теми же методами
from_data(), что и при загрузке JSON. Логика предметной области (свободные
места, выручка, скидки) остаётся в моделях, а здесь только SQL и сборка
объектов.
"""

from db.database import fetch_all, fetch_one
from models import EXCURSION_CLASSES, Excursion, Guide, Route, Schedule


def _languages(value):
    """Строка «русский, английский» превращается в список языков."""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _make_guide(row):
    data = dict(row)
    data["languages"] = _languages(data.get("languages"))
    data["is_active"] = bool(data.get("is_active"))
    return Guide.from_data(data)


def _make_route(row):
    data = dict(row)
    data["required_languages"] = _languages(data.get("required_languages"))
    data["is_active"] = bool(data.get("is_active"))
    return Route.from_data(data)


def _make_excursion(row, route):
    data = dict(row)
    data["languages"] = _languages(data.get("languages"))
    data["is_active"] = bool(data.get("is_active"))
    excursion_class = EXCURSION_CLASSES.get(data.get("kind"), Excursion)
    return excursion_class.from_data(data, route)


def _make_schedule(row, excursion, guide):
    return Schedule.from_data(dict(row), excursion, guide)


# --- гиды -----------------------------------------------------------------

def list_guides():
    """Все гиды по алфавиту."""
    return [_make_guide(row) for row in fetch_all(
        "SELECT * FROM guides ORDER BY name;"
    )]


def get_guide(guide_id):
    """Гид по идентификатору или None, если такого нет."""
    row = fetch_one("SELECT * FROM guides WHERE id = ?;", [guide_id])
    return _make_guide(row) if row else None


def list_available_guides(schedule_date):
    """Гиды, свободные на выбранную дату."""
    return [_make_guide(row) for row in fetch_all(
        "SELECT * FROM guides "
        "WHERE is_active = 1 AND id NOT IN ("
        "    SELECT guide_id FROM schedules "
        "    WHERE date = ? AND status <> 'отменена'"
        ") ORDER BY name;",
        [schedule_date],
    )]


# --- маршруты -------------------------------------------------------------

def list_routes():
    """Все маршруты по алфавиту."""
    return [_make_route(row) for row in fetch_all(
        "SELECT * FROM routes ORDER BY name;"
    )]


def get_route(route_id):
    """Маршрут по идентификатору или None."""
    row = fetch_one("SELECT * FROM routes WHERE id = ?;", [route_id])
    return _make_route(row) if row else None


# --- экскурсии ------------------------------------------------------------

def list_excursions():
    """Все экскурсии с уже найденными объектами маршрутов."""
    routes = {route.id: route for route in list_routes()}
    result = []
    for row in fetch_all("SELECT * FROM excursions ORDER BY title;"):
        route = routes.get(row["route_id"])
        if route is None:
            continue
        result.append(_make_excursion(row, route))
    return result


def get_excursion(excursion_id):
    """Экскурсия по идентификатору или None."""
    row = fetch_one("SELECT * FROM excursions WHERE id = ?;", [excursion_id])
    if row is None:
        return None
    route = get_route(row["route_id"])
    if route is None:
        return None
    return _make_excursion(row, route)


def list_excursions_by_route(route_id):
    """Экскурсии, которые проводятся по указанному маршруту."""
    return [item for item in list_excursions() if item.route.id == route_id]


# --- занятия --------------------------------------------------------------

def list_schedules(only_active=False):
    """Занятия расписания; при only_active отменённые не попадают в выборку."""
    excursions = {item.id: item for item in list_excursions()}
    guides = {item.id: item for item in list_guides()}

    sql = "SELECT * FROM schedules "
    if only_active:
        sql += "WHERE status <> 'отменена' "
    sql += "ORDER BY date, start_time;"

    result = []
    for row in fetch_all(sql):
        excursion = excursions.get(row["excursion_id"])
        guide = guides.get(row["guide_id"])
        if excursion is None or guide is None:
            continue
        result.append(_make_schedule(row, excursion, guide))
    return result


def get_schedule(schedule_id):
    """Занятие по идентификатору или None."""
    row = fetch_one("SELECT * FROM schedules WHERE id = ?;", [schedule_id])
    if row is None:
        return None
    excursion = get_excursion(row["excursion_id"])
    guide = get_guide(row["guide_id"])
    if excursion is None or guide is None:
        return None
    return _make_schedule(row, excursion, guide)


def list_schedules_by_guide(guide_id):
    """Занятия конкретного гида."""
    return [item for item in list_schedules() if item.guide.id == guide_id]
