"""Подключение к базе данных SQLite.

База проекта лежит в data/guideservice.sqlite. Здесь собраны три вещи:
путь к файлу, функция подключения с row_factory и выполнение схемы из
sql/schema.sql. Остальные модули и представления пользуются этими
функциями, чтобы не повторять настройку соединения.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "guideservice.sqlite"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection(path=DB_PATH):
    """Открыть соединение с базой.

    row_factory = sqlite3.Row позволяет обращаться к полям результата
    по имени: row["name"] вместо row[1].
    """
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    # SQLite по умолчанию не проверяет внешние ключи — включаем явно.
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_schema(path=DB_PATH):
    """Создать таблицы, выполнив скрипт sql/schema.sql."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
        script = file.read()

    connection = get_connection(path)
    try:
        connection.executescript(script)
        connection.commit()
    finally:
        connection.close()


def fetch_all(sql, params=(), path=DB_PATH):
    """Выполнить запрос и вернуть все строки."""
    connection = get_connection(path)
    try:
        return connection.execute(sql, params).fetchall()
    finally:
        connection.close()


def fetch_one(sql, params=(), path=DB_PATH):
    """Выполнить запрос и вернуть первую строку или None."""
    connection = get_connection(path)
    try:
        return connection.execute(sql, params).fetchone()
    finally:
        connection.close()


def table_names(path=DB_PATH):
    """Список таблиц базы — нужен для проверки после создания схемы."""
    rows = fetch_all(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name;",
        path=path,
    )
    return [row["name"] for row in rows]
