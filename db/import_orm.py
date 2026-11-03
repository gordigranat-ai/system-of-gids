"""Перенос данных из базы ПР7 в таблицы Django-моделей.

Стратегия перехода (ПР9, вариант 2): исходная база ПР7
(data/guideservice.sqlite) не меняется и остаётся источником, а Django
работает со своей базой из settings.DATABASES. Скрипт читает исходные
таблицы через sqlite3 и создаёт объекты моделей с теми же
идентификаторами, поэтому связи между записями сохраняются.

Запуск:

    python -m db.import_orm
"""

import os
import sqlite3
from datetime import date, time
from decimal import Decimal
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "guideservice.settings")
django.setup()

from django.db import transaction  # noqa: E402

from db.database import DB_PATH  # noqa: E402
from excursions.models import Excursion  # noqa: E402
from guides.models import Guide  # noqa: E402
from routes.models import Route  # noqa: E402
from schedules.models import Schedule, ScheduleStatus  # noqa: E402

# Статусы в базе ПР7 записаны по-русски, в моделях используются коды.
STATUS_CODES = {
    "запланирована": ScheduleStatus.ACTIVE,
    "проведена": ScheduleStatus.COMPLETED,
    "отменена": ScheduleStatus.CANCELLED,
}


def read_source():
    """Прочитать исходные таблицы ПР7 и вернуть их словарями."""
    if not Path(DB_PATH).exists():
        raise SystemExit(f"Не найдена исходная база: {DB_PATH}")

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        return {
            "guides": [dict(row) for row in connection.execute(
                "SELECT * FROM guides ORDER BY id;"
            )],
            "routes": [dict(row) for row in connection.execute(
                "SELECT * FROM routes ORDER BY id;"
            )],
            "excursions": [dict(row) for row in connection.execute(
                "SELECT * FROM excursions ORDER BY id;"
            )],
            "schedules": [dict(row) for row in connection.execute(
                "SELECT * FROM schedules ORDER BY id;"
            )],
        }
    finally:
        connection.close()


def check_links(source):
    """Проверить, что все внешние ключи указывают на существующие записи."""
    route_ids = {row["id"] for row in source["routes"]}
    excursion_ids = {row["id"] for row in source["excursions"]}
    guide_ids = {row["id"] for row in source["guides"]}

    for row in source["excursions"]:
        if row["route_id"] not in route_ids:
            raise SystemExit(
                f"Экскурсия {row['id']} ссылается на несуществующий маршрут"
            )
    for row in source["schedules"]:
        if row["excursion_id"] not in excursion_ids:
            raise SystemExit(
                f"Занятие {row['id']} ссылается на несуществующую экскурсию"
            )
        if row["guide_id"] not in guide_ids:
            raise SystemExit(
                f"Занятие {row['id']} ссылается на несуществующего гида"
            )


def clear_target():
    """Очистить таблицы в порядке от зависимых к основным."""
    Schedule.objects.all().delete()
    Excursion.objects.all().delete()
    Route.objects.all().delete()
    Guide.objects.all().delete()


def import_guides(source):
    Guide.objects.bulk_create([
        Guide(
            id=row["id"],
            name=row["name"],
            specialization=row["specialization"],
            languages=row["languages"],
            experience_years=row["experience_years"],
            rating=Decimal(str(row["rating"])),
            is_active=bool(row["is_active"]),
        )
        for row in source["guides"]
    ])
    return len(source["guides"])


def import_routes(source):
    Route.objects.bulk_create([
        Route(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            duration_hours=Decimal(str(row["duration_hours"])),
            distance_km=Decimal(str(row["distance_km"])),
            difficulty=row["difficulty"],
            required_languages=row["required_languages"] or "",
            is_active=bool(row["is_active"]),
        )
        for row in source["routes"]
    ])
    return len(source["routes"])


def import_excursions(source):
    Excursion.objects.bulk_create([
        Excursion(
            id=row["id"],
            title=row["title"],
            route_id=row["route_id"],
            kind=row["kind"],
            base_price=Decimal(str(row["base_price"])),
            max_participants=row["max_participants"],
            min_age=row["min_age"],
            languages=row["languages"] or "",
            is_active=bool(row["is_active"]),
        )
        for row in source["excursions"]
    ])
    return len(source["excursions"])


def import_schedules(source):
    Schedule.objects.bulk_create([
        Schedule(
            id=row["id"],
            excursion_id=row["excursion_id"],
            guide_id=row["guide_id"],
            date=date.fromisoformat(row["date"]),
            start_time=time.fromisoformat(row["start_time"]),
            booked=row["booked"],
            status=STATUS_CODES[row["status"]],
            note=row["note"] or "",
        )
        for row in source["schedules"]
    ])
    return len(source["schedules"])


def main():
    """Перенести данные и напечатать количество созданных записей."""
    source = read_source()
    check_links(source)

    with transaction.atomic():
        clear_target()
        counts = {
            "гидов": import_guides(source),
            "маршрутов": import_routes(source),
            "экскурсий": import_excursions(source),
            "занятий": import_schedules(source),
        }

    print("Данные перенесены из базы ПР7 в таблицы Django-моделей:")
    for name, value in counts.items():
        print(f"  {name}: {value}")

    print("\nПроверка в целевой базе:")
    print(f"  Guide:    {Guide.objects.count()}")
    print(f"  Route:    {Route.objects.count()}")
    print(f"  Excursion: {Excursion.objects.count()}")
    print(f"  Schedule: {Schedule.objects.count()}")


if __name__ == "__main__":
    main()
