"""Тесты базы данных и SQL-запросов проекта.

Проверяем, что схема создана, данные перенесены из JSON, слой выборки
возвращает объекты классов ПР3, а все запросы из sql/queries.sql
выполняются.
"""

from db.database import BASE_DIR, DB_PATH, fetch_all, fetch_one, table_names
from db.repository import get_guide, list_guides, list_schedules
from models import Guide, Schedule


def test_database_file_exists():
    """Файл базы лежит в data/ и создан."""
    assert DB_PATH.exists()
    assert DB_PATH.name == "guideservice.sqlite"


def test_schema_has_all_tables():
    """Схема содержит четыре таблицы предметной области."""
    expected = {"guides", "routes", "excursions", "schedules"}
    assert expected <= set(table_names())


def test_tables_are_filled():
    """Данные перенесены из JSON: в каждой таблице есть записи."""
    for table in ("guides", "routes", "excursions", "schedules"):
        row = fetch_one(f"SELECT COUNT(*) AS count FROM {table};")
        assert row["count"] > 0, table


def test_foreign_keys_are_enabled():
    """Соединение включает проверку внешних ключей."""
    assert fetch_one("PRAGMA foreign_keys;")[0] == 1


def test_repository_returns_domain_objects():
    """Выборка из базы даёт объекты классов, а не словари."""
    guides = list_guides()
    schedules = list_schedules()

    assert guides and all(isinstance(item, Guide) for item in guides)
    assert schedules and all(isinstance(item, Schedule) for item in schedules)


def test_missing_guide_returns_none():
    """Несуществующий идентификатор даёт None, а не исключение."""
    assert get_guide(9999) is None


def test_schedule_links_are_restored():
    """Связи занятия восстанавливаются: есть экскурсия, гид и маршрут."""
    for item in list_schedules():
        assert item.excursion is not None
        assert item.guide is not None
        assert item.route is not None


def test_queries_file_executes():
    """Каждый запрос из sql/queries.sql выполняется без ошибок."""
    sql_text = (BASE_DIR / "sql" / "queries.sql").read_text(encoding="utf-8")
    statements = [part.strip() for part in sql_text.split(";") if part.strip()]

    assert len(statements) >= 8
    for statement in statements:
        assert fetch_all(statement) is not None


def test_group_by_query_counts_schedules():
    """Запрос с GROUP BY считает занятия по гидам."""
    rows = fetch_all(
        "SELECT g.name, COUNT(s.id) AS schedules_count "
        "FROM guides AS g "
        "LEFT JOIN schedules AS s "
        "       ON s.guide_id = g.id AND s.status <> 'отменена' "
        "GROUP BY g.id, g.name ORDER BY schedules_count DESC;"
    )

    assert len(rows) == len(list_guides())
    assert all(row["schedules_count"] >= 0 for row in rows)


def test_available_guides_query_excludes_busy():
    """Запрос NOT IN не показывает гидов, занятых в выбранный день."""
    busy = fetch_one(
        "SELECT guide_id FROM schedules "
        "WHERE date = '2026-03-10' AND status <> 'отменена' LIMIT 1;"
    )
    assert busy is not None

    rows = fetch_all(
        "SELECT id FROM guides "
        "WHERE is_active = 1 AND id NOT IN ("
        "  SELECT guide_id FROM schedules "
        "  WHERE date = '2026-03-10' AND status <> 'отменена'"
        ");"
    )
    free_ids = {row["id"] for row in rows}
    assert busy["guide_id"] not in free_ids
