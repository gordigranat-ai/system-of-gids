-- ==========================================================
-- Сервис управления гидами: SQL-запросы проекта
-- База: data/guideservice.sqlite
-- ==========================================================
--
-- Запросы соответствуют задачам веб-интерфейса: списки, отбор,
-- соединение таблиц, подсчёт и группировка.
--
-- В файле приведены готовые запросы с конкретными значениями — их можно
-- выполнить в sqlite3 и увидеть результат. В Django-представлениях те же
-- запросы выполняются с заполнителями ?, а значения передаются отдельно:
-- это параметризованные запросы, данные пользователя не попадают в текст SQL.


-- 1. Список гидов
-- Страница «Гиды»: все гиды справочника по алфавиту.
SELECT
    id,
    name,
    specialization,
    languages,
    experience_years,
    rating,
    is_active
FROM guides
ORDER BY name;


-- 2. Отбор гидов по языку и стажу
-- WHERE + LIKE + сравнение: активные гиды, знающие английский,
-- со стажем не меньше пяти лет.
SELECT
    name,
    languages,
    experience_years,
    rating
FROM guides
WHERE languages LIKE '%английский%'
  AND experience_years >= 5
  AND is_active = 1
ORDER BY experience_years DESC;


-- 3. Активные занятия расписания
-- JOIN трёх таблиц: занятие + экскурсия + гид.
-- Отменённые занятия в список не попадают.
SELECT
    s.date,
    s.start_time,
    e.title AS excursion,
    g.name AS guide,
    s.booked,
    s.status
FROM schedules AS s
JOIN excursions AS e ON e.id = s.excursion_id
JOIN guides AS g ON g.id = s.guide_id
WHERE s.status <> 'отменена'
ORDER BY s.date, s.start_time;


-- 4. Полная информация о занятии
-- JOIN четырёх таблиц: занятие, экскурсия, маршрут и гид.
-- Такую строку показывает карточка занятия.
SELECT
    s.id,
    s.date,
    s.start_time,
    e.title AS excursion,
    e.base_price,
    r.name AS route,
    r.duration_hours,
    g.name AS guide,
    g.specialization,
    s.booked,
    s.status
FROM schedules AS s
JOIN excursions AS e ON e.id = s.excursion_id
JOIN routes AS r ON r.id = e.route_id
JOIN guides AS g ON g.id = s.guide_id
WHERE s.id = 1;


-- 5. Гиды, свободные на выбранную дату
-- Подзапрос NOT IN: берём активных гидов, которых нет среди занятых
-- в этот день. Отменённое занятие гида не занимает.
SELECT
    g.id,
    g.name,
    g.specialization,
    g.experience_years
FROM guides AS g
WHERE g.is_active = 1
  AND g.id NOT IN (
      SELECT s.guide_id
      FROM schedules AS s
      WHERE s.date = '2026-03-10'
        AND s.status <> 'отменена'
  )
ORDER BY g.name;


-- 6. Количество активных занятий
-- Агрегатная функция COUNT.
SELECT COUNT(*) AS active_schedules
FROM schedules
WHERE status <> 'отменена';


-- 7. Количество занятий по гидам
-- GROUP BY: LEFT JOIN сохраняет в выборке гидов без занятий,
-- у них COUNT(s.id) равен нулю.
SELECT
    g.name,
    COUNT(s.id) AS schedules_count
FROM guides AS g
LEFT JOIN schedules AS s
       ON s.guide_id = g.id
      AND s.status <> 'отменена'
GROUP BY g.id, g.name
ORDER BY schedules_count DESC, g.name;


-- 8. Гиды, у которых больше одного занятия
-- HAVING фильтрует уже сгруппированные строки, WHERE — исходные.
-- Порог можно поменять: HAVING COUNT(s.id) > 2.
SELECT
    g.name,
    COUNT(s.id) AS schedules_count
FROM guides AS g
JOIN schedules AS s ON s.guide_id = g.id
WHERE s.status <> 'отменена'
GROUP BY g.id, g.name
HAVING COUNT(s.id) > 1
ORDER BY schedules_count DESC;


-- 9. Выручка и заполняемость по экскурсиям
-- SUM и AVG вместе с GROUP BY: сколько занятий, сколько мест продано,
-- какая выручка и средняя заполняемость в процентах.
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


-- 10. Пять ближайших занятий
-- ORDER BY вместе с LIMIT: сортировка и ограничение выборки.
SELECT
    s.date,
    s.start_time,
    e.title AS excursion,
    g.name AS guide
FROM schedules AS s
JOIN excursions AS e ON e.id = s.excursion_id
JOIN guides AS g ON g.id = s.guide_id
WHERE s.status <> 'отменена'
ORDER BY s.date, s.start_time
LIMIT 5;


-- 11. Сводка по базе для страницы статистики
-- Несколько COUNT в одном запросе.
SELECT
    (SELECT COUNT(*) FROM guides) AS guides,
    (SELECT COUNT(*) FROM routes) AS routes,
    (SELECT COUNT(*) FROM excursions) AS excursions,
    (SELECT COUNT(*) FROM schedules) AS schedules,
    (SELECT COUNT(*) FROM schedules WHERE status <> 'отменена')
        AS active_schedules;
