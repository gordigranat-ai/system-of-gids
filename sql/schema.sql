-- СУБД: SQLite. Файл базы: data/guideservice.sqlite
-- Таблицы повторяют сущности предметной области ПР3:
-- гид, маршрут, экскурсия, занятие расписания.
-- Связанные записи ссылаются друг на друга внешними ключами:
-- excursions.route_id        -> routes.id
-- schedules.excursion_id     -> excursions.id
-- schedules.guide_id         -> guides.id
--
-- Списки строк (языки) хранятся в одном поле через запятую:
-- так их можно отбирать условием LIKE.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS guides (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    languages TEXT NOT NULL,
    experience_years INTEGER NOT NULL DEFAULT 0,
    rating REAL NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS routes (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    duration_hours REAL NOT NULL,
    distance_km REAL NOT NULL DEFAULT 0,
    difficulty TEXT NOT NULL,
    required_languages TEXT,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS excursions (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    route_id INTEGER NOT NULL,
    kind TEXT NOT NULL DEFAULT 'обычная экскурсия',
    base_price REAL NOT NULL,
    max_participants INTEGER NOT NULL,
    min_age INTEGER NOT NULL DEFAULT 0,
    languages TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (route_id) REFERENCES routes (id)
);

CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY,
    excursion_id INTEGER NOT NULL,
    guide_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    booked INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'запланирована',
    note TEXT,
    FOREIGN KEY (excursion_id) REFERENCES excursions (id),
    FOREIGN KEY (guide_id) REFERENCES guides (id)
);

-- Индексы по внешним ключам и по дате: по ним идут выборки страниц.
CREATE INDEX IF NOT EXISTS idx_excursions_route ON excursions (route_id);
CREATE INDEX IF NOT EXISTS idx_schedules_excursion ON schedules (excursion_id);
CREATE INDEX IF NOT EXISTS idx_schedules_guide ON schedules (guide_id);
CREATE INDEX IF NOT EXISTS idx_schedules_date ON schedules (date);
