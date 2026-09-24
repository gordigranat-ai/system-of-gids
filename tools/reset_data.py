"""Вернуть демонстрационные данные проекта.

После экспериментов с меню данные в data/ меняются. Скрипт создаёт объекты
классов Guide, Route, Excursion (и FamilyExcursion) и Schedule и сохраняет
их в JSON — то есть проходит тот же путь, что и программа при выходе.

Запуск: python tools/reset_demo_data.py
"""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Excursion, FamilyExcursion, Guide, Route, Schedule
from storage import save_all


def build_guides():
    """Демонстрационный справочник гидов."""
    return [
        Guide(1, "Анна Смирнова", "городская экскурсия", ["русский", "английский"], 7, 4.8),
        Guide(2, "Игорь Петров", "музейная экскурсия", ["русский", "немецкий"], 12, 4.9),
        Guide(3, "Мария Ковалёва", "природная экскурсия",
              ["русский", "английский", "французский"], 4, 4.6),
        Guide(4, "Дмитрий Волков", "гастрономическая экскурсия", ["русский"], 2, 4.3),
        Guide(5, "Ольга Никитина", "детская экскурсия", ["русский", "английский"], 9, 4.7, False),
    ]


def build_routes():
    """Демонстрационный справочник маршрутов."""
    return [
        Route(1, "Исторический центр", 2.5, "лёгкий",
              "Пешая прогулка по главным площадям и улицам исторического центра.",
              distance_km=3.5, required_languages=["русский", "английский"]),
        Route(2, "Музейный квартал", 3.0, "лёгкий",
              "Посещение трёх музеев квартала с рассказом о коллекциях.",
              distance_km=1.8, required_languages=["русский"]),
        Route(3, "Парковый маршрут у реки", 4.0, "средний",
              "Прогулка по набережной и парковой зоне со смотровыми площадками.",
              distance_km=8.4, required_languages=["русский", "английский"]),
        Route(4, "Гастрономический маршрут", 3.5, "лёгкий",
              "Знакомство с местной кухней: рынок, сыроварня, дегустация.",
              distance_km=2.6, required_languages=["русский"]),
        Route(5, "Горный маршрут выходного дня", 7.0, "сложный",
              "Подъём к панорамной точке, протяжённый маршрут с перепадом высот.",
              distance_km=15.2, required_languages=["русский"], is_active=False),
    ]


def build_excursions(routes):
    """Демонстрационный справочник экскурсий.

    Экскурсия № 5 — семейная, поэтому создаётся объектом FamilyExcursion.
    """
    by_id = {route.id: route for route in routes}
    return [
        Excursion(1, "Знакомство с городом", by_id[1], 15, 1800.0),
        Excursion(2, "Три музея за один день", by_id[2], 12, 2400.0, min_age=12),
        Excursion(3, "Набережная и парки", by_id[3], 20, 1500.0, min_age=6),
        Excursion(4, "Вкус города", by_id[4], 10, 3200.0, min_age=18),
        FamilyExcursion(5, "Детская прогулка по парку", by_id[3], 25, 1200.0, min_age=4),
    ]


def build_schedules(excursions, guides):
    """Демонстрационное расписание: занятие связывает экскурсию и гида."""
    by_excursion = {item.id: item for item in excursions}
    by_guide = {item.id: item for item in guides}
    return [
        Schedule(1, by_excursion[1], by_guide[1], date(2026, 3, 10), "10:00", booked=8,
                 note="Группа туристов из гостиницы «Центральная»"),
        Schedule(2, by_excursion[2], by_guide[2], date(2026, 3, 10), "12:00", booked=12,
                 note="Школьная группа"),
        Schedule(3, by_excursion[3], by_guide[3], date(2026, 3, 11), "11:00", booked=5),
        Schedule(4, by_excursion[4], by_guide[4], date(2026, 3, 12), "18:00", booked=6,
                 note="Дегустация для корпоративной группы"),
        Schedule(5, by_excursion[1], by_guide[1], date(2026, 3, 13), "10:00", booked=15,
                 status="проведена", note="Мест не осталось"),
        Schedule(6, by_excursion[5], by_guide[3], date(2026, 3, 14), "09:30", booked=10,
                 note="Семейная группа"),
        Schedule(7, by_excursion[3], by_guide[3], date(2026, 3, 14), "13:00",
                 status="отменена", note="Отменена из-за погоды"),
        Schedule(8, by_excursion[2], by_guide[2], date(2026, 3, 15), "12:30", booked=4),
    ]


def main():
    """Создать объекты и сохранить их в файлы данных."""
    print("Восстанавливаю демонстрационные данные проекта...")
    guides = build_guides()
    routes = build_routes()
    excursions = build_excursions(routes)
    schedules = build_schedules(excursions, guides)
    counts = save_all(guides, routes, excursions, schedules)
    print(f"  Создано объектов: {counts}")
    print("  Файлы каталога data/ приведены к исходному состоянию.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
