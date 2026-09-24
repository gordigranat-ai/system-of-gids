"""Загрузка и сохранение данных проекта.

В файлах JSON лежат обычные данные, поэтому при загрузке словари
превращаются в объекты классов, а при сохранении объекты — обратно
в словари. Связанные объекты хранятся идентификаторами: у экскурсии
route_id, у занятия excursion_id и guide_id. При загрузке по ним
находятся нужные объекты и ссылки восстанавливаются.

Файлы читаем и пишем через with. Если файла нет — начинаем с пустых
списков, если JSON испорчен — возбуждаем StorageError.
"""

import json
import os

from models import EXCURSION_CLASSES, Excursion, Guide, Route, Schedule, StorageError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

GUIDES_FILE = os.path.join(DATA_DIR, "guides.json")
ROUTES_FILE = os.path.join(DATA_DIR, "routes.json")
EXCURSIONS_FILE = os.path.join(DATA_DIR, "excursions.json")
SCHEDULES_FILE = os.path.join(DATA_DIR, "schedules.json")


def read_json(filename):
    """Прочитать список записей из файла."""
    if not os.path.exists(filename):
        print(f"  Файла {os.path.basename(filename)} нет, начнём с пустого списка")
        return []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        raise StorageError(f"Файл {os.path.basename(filename)} испорчен")
    except OSError as error:
        raise StorageError(f"Не удалось прочитать файл: {error}")

    if not isinstance(data, list):
        raise StorageError(f"Файл {os.path.basename(filename)} должен содержать список")
    return data


def write_json(filename, data):
    """Записать данные в файл."""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
    except OSError as error:
        raise StorageError(f"Не удалось сохранить файл: {error}")


def load_guides(filename=GUIDES_FILE):
    """Загрузить гидов."""
    guides = []
    for data in read_json(filename):
        try:
            guides.append(Guide.from_data(data))
        except (ValueError, TypeError) as error:
            print(f"  Пропущена запись гида: {error}")
    return guides


def save_guides(guides, filename=GUIDES_FILE):
    """Сохранить гидов."""
    write_json(filename, [guide.attributes() for guide in guides])
    return len(guides)


def load_routes(filename=ROUTES_FILE):
    """Загрузить маршруты."""
    routes = []
    for data in read_json(filename):
        try:
            routes.append(Route.from_data(data))
        except (ValueError, TypeError) as error:
            print(f"  Пропущена запись маршрута: {error}")
    return routes


def save_routes(routes, filename=ROUTES_FILE):
    """Сохранить маршруты."""
    write_json(filename, [route.attributes() for route in routes])
    return len(routes)


def load_excursions(routes, filename=EXCURSIONS_FILE):
    """Загрузить экскурсии, найдя для каждой её маршрут по route_id."""
    excursions = []
    for data in read_json(filename):
        route = None
        for item in routes:
            if item.id == data.get("route_id"):
                route = item
        if route is None:
            print(f"  Пропущена экскурсия № {data.get('id')}: маршрут не найден")
            continue

        excursion_class = EXCURSION_CLASSES.get(data.get("kind"), Excursion)
        excursions.append(excursion_class.from_data(data, route))
    return excursions


def save_excursions(excursions, filename=EXCURSIONS_FILE):
    """Сохранить экскурсии."""
    write_json(filename, [excursion.attributes() for excursion in excursions])
    return len(excursions)


def load_schedules(excursions, guides, filename=SCHEDULES_FILE):
    """Загрузить занятия, восстановив ссылки на экскурсию и гида."""
    schedules = []
    for data in read_json(filename):
        excursion = None
        for item in excursions:
            if item.id == data.get("excursion_id"):
                excursion = item
        guide = None
        for item in guides:
            if item.id == data.get("guide_id"):
                guide = item
        if excursion is None or guide is None:
            print(f"  Пропущено занятие № {data.get('id')}: нет экскурсии или гида")
            continue

        schedules.append(Schedule.from_data(data, excursion, guide))
    return schedules


def save_schedules(schedules, filename=SCHEDULES_FILE):
    """Сохранить расписание."""
    write_json(filename, [item.attributes() for item in schedules])
    return len(schedules)


def save_all(guides, routes, excursions, schedules):
    """Сохранить все данные сразу."""
    return {
        "guides": save_guides(guides),
        "routes": save_routes(routes),
        "excursions": save_excursions(excursions),
        "schedules": save_schedules(schedules),
    }


def load_all():
    """Загрузить всё: сначала маршруты, потом экскурсии, потом занятия."""
    guides = load_guides()
    routes = load_routes()
    excursions = load_excursions(routes)
    schedules = load_schedules(excursions, guides)
    return guides, routes, excursions, schedules


def storage_summary():
    """Список файлов данных: имя, размер, есть ли файл."""
    summary = []
    for filename in (GUIDES_FILE, ROUTES_FILE, EXCURSIONS_FILE, SCHEDULES_FILE):
        exists = os.path.exists(filename)
        size = f"{os.path.getsize(filename)} Б" if exists else "—"
        summary.append((os.path.basename(filename), size, exists))
    return summary
