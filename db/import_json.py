"""Перенос данных проекта из JSON-файлов в базу SQLite.

Данные читаются теми же функциями ПР3 (storage.load_all), поэтому в базу
попадают уже проверенные объекты предметной области. Списки строк
(языки) склеиваются в одну строку через запятую: так по ним можно
отбирать условием LIKE.

Запуск:

    python -m db.import_json
"""

from db.database import create_schema, get_connection
from storage import load_all


def _languages(items):
    """Список языков в одну строку: «русский, английский»."""
    return ", ".join(items or [])


def _import_guides(connection, guides):
    connection.executemany(
        "INSERT INTO guides (id, name, specialization, languages, "
        "experience_years, rating, is_active) "
        "VALUES (?, ?, ?, ?, ?, ?, ?);",
        [
            (
                guide.id,
                guide.name,
                guide.specialization,
                _languages(guide.languages),
                guide.experience_years,
                guide.rating,
                int(bool(guide.is_active)),
            )
            for guide in guides
        ],
    )


def _import_routes(connection, routes):
    connection.executemany(
        "INSERT INTO routes (id, name, description, duration_hours, "
        "distance_km, difficulty, required_languages, is_active) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
        [
            (
                route.id,
                route.name,
                route.description,
                route.duration_hours,
                route.distance_km,
                route.difficulty,
                _languages(route.required_languages),
                int(bool(route.is_active)),
            )
            for route in routes
        ],
    )


def _import_excursions(connection, excursions):
    connection.executemany(
        "INSERT INTO excursions (id, title, route_id, kind, base_price, "
        "max_participants, min_age, languages, is_active) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
        [
            (
                excursion.id,
                excursion.title,
                excursion.route.id,
                excursion.kind,
                excursion.base_price,
                excursion.max_participants,
                excursion.min_age,
                _languages(excursion.languages),
                int(bool(excursion.is_active)),
            )
            for excursion in excursions
        ],
    )


def _import_schedules(connection, schedules):
    connection.executemany(
        "INSERT INTO schedules (id, excursion_id, guide_id, date, "
        "start_time, booked, status, note) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
        [
            (
                item.id,
                item.excursion.id,
                item.guide.id,
                item.date,
                item.start_time,
                item.booked,
                item.status,
                item.note,
            )
            for item in schedules
        ],
    )


def clear_tables(connection):
    """Очистить таблицы, начиная с зависимых."""
    for table in ("schedules", "excursions", "routes", "guides"):
        connection.execute(f"DELETE FROM {table};")


def import_all():
    """Создать схему (если нужно) и залить данные из JSON."""
    create_schema()

    guides, routes, excursions, schedules = load_all()

    connection = get_connection()
    try:
        with connection:
            clear_tables(connection)
            # Порядок важен: сначала таблицы, на которые ссылаются другие.
            _import_guides(connection, guides)
            _import_routes(connection, routes)
            _import_excursions(connection, excursions)
            _import_schedules(connection, schedules)
    finally:
        connection.close()

    return {
        "guides": len(guides),
        "routes": len(routes),
        "excursions": len(excursions),
        "schedules": len(schedules),
    }


def main():
    """Точка входа: перенести данные и напечатать, сколько записей попало в базу."""
    counts = import_all()
    print("Данные перенесены в базу SQLite:")
    for name, value in counts.items():
        print(f"  {name}: {value}")


if __name__ == "__main__":
    main()
