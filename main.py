"""Главный файл программы «Сервис управления туристическими гидами».

Здесь меню, сценарии из ПР1 и точка входа. Классы и правила предметной
области лежат в models.py, работа с файлами — в storage.py,
вспомогательные функции — в utils.py.

Запуск: python main.py
"""

from models import (
    DIFFICULTIES,
    SPECIALIZATIONS,
    Guide,
    GuideServiceError,
    add_excursion,
    add_guide,
    add_route,
    add_schedule,
    book_seats,
    cancel_schedule,
    cancel_seats,
    create_schedule,
    filter_available_schedules,
    filter_excursions_by_price,
    filter_excursions_by_route,
    filter_excursions_for_children,
    filter_excursions_for_group,
    filter_guides_by_experience,
    filter_guides_by_language,
    filter_guides_by_specialization,
    filter_routes_by_difficulty,
    filter_routes_by_duration,
    filter_schedules_by_date,
    filter_schedules_by_guide,
    filter_schedules_by_period,
    find_guide_conflicts,
    find_schedule,
    get_excursion,
    get_guide,
    get_route,
    mark_schedule_done,
    remove_excursion,
    remove_guide,
    remove_route,
    search_excursions,
    search_guides,
    search_routes,
    sort_excursions,
    sort_guides,
    sort_routes,
)
from statistics import (
    build_summary,
    count_schedules_by_guide,
    count_schedules_by_route,
    occupancy_report,
    summary_line,
    total_revenue,
    weekday_activity,
)
from storage import StorageError, load_all, save_all
from utils import (
    format_date,
    input_choice,
    input_date,
    input_float,
    input_int,
    input_required,
    input_time,
    input_yes_no,
    print_header,
    print_table,
    show_excursions,
    show_guides,
    show_routes,
    show_schedules,
    split_list,
)


# --- меню гидов -----------------------------------------------------------

def add_guide_dialog(guides):
    """Спросить данные и создать гида."""
    name = input_required("  Имя гида: ")
    specialization = input_choice(
        "  Специализация (" + ", ".join(SPECIALIZATIONS) + "): ", SPECIALIZATIONS)
    languages = input_required("  Языки через запятую: ")
    experience = input_int("  Стаж работы (лет): ", minimum=0, maximum=70)
    rating = input_float("  Рейтинг (0-5): ", minimum=0, maximum=5)

    guide = Guide(len(guides) + 1, name, specialization, split_list(languages),
                  experience, rating)
    add_guide(guides, guide)
    print(f"\n  Гид добавлен, id = {guide.id}")
    print(f"  {guide}")


def guides_menu(guides):
    """Меню гидов."""
    while True:
        print_header("ГИДЫ")
        print("  1. Показать всех гидов")
        print("  2. Найти гида по имени")
        print("  3. Отобрать по языку")
        print("  4. Отобрать по специализации")
        print("  5. Отобрать по стажу")
        print("  6. Отсортировать")
        print("  7. Добавить гида")
        print("  8. Удалить гида")
        print("  0. Назад")
        try:
            choice = input("  Выберите действие: ").strip()
            if choice == "0":
                return
            elif choice == "1":
                show_guides(guides)
            elif choice == "2":
                query = input_required("  Часть имени: ")
                show_guides(search_guides(guides, query), f"Поиск: {query}")
            elif choice == "3":
                language = input_required("  Язык: ")
                found = filter_guides_by_language(guides, language)
                show_guides(found, f"Знают язык {language}")
            elif choice == "4":
                specialization = input_choice(
                    "  Специализация (" + ", ".join(SPECIALIZATIONS) + "): ",
                    SPECIALIZATIONS)
                found = filter_guides_by_specialization(guides, specialization)
                show_guides(found, f"Специализация: {specialization}")
            elif choice == "5":
                minimum = input_int("  Минимальный стаж: ", minimum=0, maximum=70)
                show_guides(filter_guides_by_experience(guides, minimum),
                            f"Стаж от {minimum} лет")
            elif choice == "6":
                field = input_choice("  Поле сортировки (имя, стаж, рейтинг): ",
                                     ("имя", "стаж", "рейтинг"))
                found = sort_guides(guides, field, reverse=(field != "имя"))
                show_guides(found, f"Сортировка по полю {field}")
            elif choice == "7":
                add_guide_dialog(guides)
            elif choice == "8":
                guide = get_guide(guides, input_int("  Id гида: ", minimum=1))
                if input_yes_no(f"  Удалить гида «{guide.name}»?"):
                    remove_guide(guides, guide.id)
                    print("  Гид удалён.")
            else:
                print("  Такого пункта нет.")
        except GuideServiceError as error:
            print(f"\n  Ошибка: {error}")
        except ValueError as error:
            print(f"\n  Ошибка ввода: {error}")


# --- меню маршрутов -------------------------------------------------------

def add_route_dialog(routes):
    """Спросить данные и создать маршрут."""
    name = input_required("  Название маршрута: ")
    duration = input_float("  Продолжительность (часов): ", minimum=0.5, maximum=24)
    difficulty = input_choice("  Сложность (" + ", ".join(DIFFICULTIES) + "): ",
                              DIFFICULTIES)
    distance = input_float("  Протяжённость (км): ", minimum=0, maximum=500)
    description = input_required("  Краткое описание: ")
    languages = input_required("  Языки маршрута через запятую: ")

    route = create_route(routes, name, duration, difficulty, description,
                         distance, split_list(languages))
    print(f"\n  Маршрут добавлен, id = {route.id}")
    print(f"  {route}")


def routes_menu(routes, excursions):
    """Меню маршрутов."""
    while True:
        print_header("МАРШРУТЫ")
        print("  1. Показать все маршруты")
        print("  2. Найти по названию или описанию")
        print("  3. Отобрать по сложности")
        print("  4. Отобрать по продолжительности")
        print("  5. Отсортировать")
        print("  6. Добавить маршрут")
        print("  7. Удалить маршрут")
        print("  0. Назад")
        try:
            choice = input("  Выберите действие: ").strip()
            if choice == "0":
                return
            elif choice == "1":
                show_routes(routes)
            elif choice == "2":
                query = input_required("  Часть названия или описания: ")
                show_routes(search_routes(routes, query), f"Поиск: {query}")
            elif choice == "3":
                difficulty = input_choice(
                    "  Сложность (" + ", ".join(DIFFICULTIES) + "): ", DIFFICULTIES)
                found = filter_routes_by_difficulty(routes, difficulty)
                show_routes(found, f"Сложность: {difficulty}")
            elif choice == "4":
                limit = input_float("  Максимум часов: ", minimum=0.5, maximum=24)
                show_routes(filter_routes_by_duration(routes, limit),
                            f"До {limit} часов")
            elif choice == "5":
                field = input_choice("  Поле сортировки (название, длительность): ",
                                     ("название", "длительность"))
                show_routes(sort_routes(routes, field), f"Сортировка по полю {field}")
            elif choice == "6":
                add_route_dialog(routes)
            elif choice == "7":
                route = get_route(routes, input_int("  Id маршрута: ", minimum=1))
                used = [item for item in excursions if item.route.id == route.id]
                if used:
                    print("  По маршруту есть экскурсии, сначала удалите их.")
                elif input_yes_no(f"  Удалить маршрут «{route.name}»?"):
                    remove_route(routes, route.id)
                    print("  Маршрут удалён.")
            else:
                print("  Такого пункта нет.")
        except GuideServiceError as error:
            print(f"\n  Ошибка: {error}")
        except ValueError as error:
            print(f"\n  Ошибка ввода: {error}")


# --- меню экскурсий -------------------------------------------------------

def add_excursion_dialog(excursions, routes):
    """Спросить данные и создать экскурсию."""
    if not routes:
        print("  Сначала нужен маршрут.")
        return

    show_routes(routes, "Доступные маршруты")
    route = get_route(routes, input_int("  Id маршрута: ", minimum=1))
    title = input_required("  Название экскурсии: ")
    price = input_float("  Цена за человека: ", minimum=1, maximum=100000)
    participants = input_int("  Максимум участников: ", minimum=1, maximum=100)
    min_age = input_int("  Минимальный возраст: ", minimum=0, maximum=18)
    languages = input_required("  Языки через запятую: ")
    family = input_yes_no("  Семейная экскурсия (детям скидка)?")

    excursion = add_excursion(excursions, title, route, price, participants,
                              split_list(languages), min_age, family)
    print(f"\n  Экскурсия добавлена, id = {excursion.id}")
    print(f"  {excursion}")


def excursions_menu(excursions, routes, schedules):
    """Меню экскурсий."""
    while True:
        print_header("ЭКСКУРСИИ")
        print("  1. Показать все экскурсии")
        print("  2. Найти по названию")
        print("  3. Отобрать по цене")
        print("  4. Отобрать по маршруту")
        print("  5. Отобрать для группы")
        print("  6. Отобрать для детей")
        print("  7. Отсортировать")
        print("  8. Посчитать стоимость для группы")
        print("  9. Добавить экскурсию")
        print("  10. Удалить экскурсию")
        print("  0. Назад")
        try:
            choice = input("  Выберите действие: ").strip()
            if choice == "0":
                return
            elif choice == "1":
                show_excursions(excursions)
            elif choice == "2":
                query = input_required("  Часть названия: ")
                show_excursions(search_excursions(excursions, query),
                                f"Поиск: {query}")
            elif choice == "3":
                limit = input_float("  Максимальная цена: ", minimum=1, maximum=100000)
                show_excursions(filter_excursions_by_price(excursions, limit),
                                f"Дешевле {limit} рублей")
            elif choice == "4":
                show_routes(routes, "Маршруты")
                route_id = input_int("  Id маршрута: ", minimum=1)
                show_excursions(filter_excursions_by_route(excursions, route_id),
                                "Экскурсии по маршруту")
            elif choice == "5":
                group_size = input_int("  Размер группы: ", minimum=1, maximum=100)
                found = filter_excursions_for_group(excursions, group_size)
                show_excursions(found, f"Подходят для группы из {group_size} человек")
            elif choice == "6":
                show_excursions(filter_excursions_for_children(excursions),
                                "Экскурсии для детей")
            elif choice == "7":
                field = input_choice("  Поле сортировки (название, цена): ",
                                     ("название", "цена"))
                show_excursions(sort_excursions(excursions, field),
                                f"Сортировка по полю {field}")
            elif choice == "8":
                excursion = get_excursion(excursions,
                                          input_int("  Id экскурсии: ", minimum=1))
                group_size = input_int("  Количество участников: ",
                                       minimum=1, maximum=100)
                age = input_int("  Возраст участника: ", minimum=0, maximum=110)
                print(f"\n  Цена за человека: {excursion.price_per_person(age)}")
                print(f"  Итого за группу: {excursion.total_price(group_size, age)}")
            elif choice == "9":
                add_excursion_dialog(excursions, routes)
            elif choice == "10":
                excursion = get_excursion(excursions,
                                          input_int("  Id экскурсии: ", minimum=1))
                planned = [item for item in schedules
                           if item.excursion.id == excursion.id]
                if planned:
                    print("  Экскурсия стоит в расписании, сначала отмените занятия.")
                elif input_yes_no(f"  Удалить экскурсию «{excursion.title}»?"):
                    remove_excursion(excursions, excursion.id)
                    print("  Экскурсия удалена.")
            else:
                print("  Такого пункта нет.")
        except GuideServiceError as error:
            print(f"\n  Ошибка: {error}")
        except ValueError as error:
            print(f"\n  Ошибка ввода: {error}")


# --- меню расписания ------------------------------------------------------

def add_schedule_dialog(schedules, excursions, guides):
    """Спросить данные и поставить занятие в расписание."""
    if not excursions or not guides:
        print("  Нужны хотя бы одна экскурсия и один гид.")
        return

    show_excursions(excursions, "Доступные экскурсии")
    excursion = get_excursion(excursions, input_int("  Id экскурсии: ", minimum=1))

    show_guides(guides, "Доступные гиды")
    guide = get_guide(guides, input_int("  Id гида: ", minimum=1))

    schedule_date = input_date("  Дата (ДД.ММ.ГГГГ): ")
    start_time = input_time("  Время начала (ЧЧ:ММ): ")
    note = input_required("  Примечание: ")

    schedule = create_schedule(schedules, excursion, guide, schedule_date,
                               start_time, note)
    print(f"\n  Занятие добавлено, id = {schedule.id}")
    print(f"  {schedule}")


def check_guide_dialog(schedules, excursions, guides):
    """Проверить, свободен ли гид (сценарий из ПР1)."""
    guide = get_guide(guides, input_int("  Id гида: ", minimum=1))
    excursion = get_excursion(excursions, input_int("  Id экскурсии: ", minimum=1))
    schedule_date = input_date("  Дата (ДД.ММ.ГГГГ): ")
    start_time = input_time("  Время начала (ЧЧ:ММ): ")

    conflicts = find_guide_conflicts(schedules, guide, schedule_date, start_time)
    languages_ok = guide.knows_languages(excursion.route.required_languages)

    print(f"\n  Гид: {guide}")
    print(f"  Экскурсия: {excursion}")
    print(f"  Дата и время: {format_date(schedule_date)} {start_time}")
    print(f"  Языки маршрута: {'подходят' if languages_ok else 'не подходят'}")
    print(f"  Статус: {guide.get_status(is_busy=bool(conflicts))}")
    for item in conflicts:
        print(f"    Пересечение с занятием № {item.id} ({item.start_time})")


def schedules_menu(schedules, excursions, guides, routes):
    """Меню расписания."""
    while True:
        print_header("РАСПИСАНИЕ")
        print("  1. Показать всё расписание")
        print("  2. Показать на дату")
        print("  3. Показать занятия гида")
        print("  4. Показать за период")
        print("  5. Показать со свободными местами")
        print("  6. Проверить доступность гида")
        print("  7. Добавить занятие")
        print("  8. Забронировать места")
        print("  9. Отменить бронирование мест")
        print("  10. Отменить занятие")
        print("  11. Отметить как проведённое")
        print("  0. Назад")
        try:
            choice = input("  Выберите действие: ").strip()
            if choice == "0":
                return
            elif choice == "1":
                show_schedules(schedules)
            elif choice == "2":
                schedule_date = input_date("  Дата (ДД.ММ.ГГГГ): ")
                found = filter_schedules_by_date(schedules, schedule_date)
                show_schedules(found, f"Расписание на {format_date(schedule_date)}")
            elif choice == "3":
                guide_id = input_int("  Id гида: ", minimum=1)
                show_schedules(filter_schedules_by_guide(schedules, guide_id),
                               "Занятия гида")
            elif choice == "4":
                date_from = input_date("  Начало периода (ДД.ММ.ГГГГ): ")
                date_to = input_date("  Конец периода (ДД.ММ.ГГГГ): ")
                found = filter_schedules_by_period(schedules, date_from, date_to)
                show_schedules(found, "Занятия за период")
            elif choice == "5":
                show_schedules(filter_available_schedules(schedules),
                               "Есть свободные места")
            elif choice == "6":
                check_guide_dialog(schedules, excursions, guides)
            elif choice == "7":
                add_schedule_dialog(schedules, excursions, guides)
            elif choice == "8":
                show_schedules(filter_available_schedules(schedules),
                               "Свободные места")
                schedule_id = input_int("  Id занятия: ", minimum=1)
                group_size = input_int("  Сколько мест: ", minimum=1, maximum=100)
                schedule = book_seats(schedules, schedule_id, group_size)
                print(f"  Занято мест: {schedule.booked}, "
                      f"свободно: {schedule.free_seats}")
            elif choice == "9":
                show_schedules(schedules, "Все занятия")
                schedule_id = input_int("  Id занятия: ", minimum=1)
                group_size = input_int("  Сколько мест отменить: ",
                                       minimum=1, maximum=100)
                schedule = cancel_seats(schedules, schedule_id, group_size)
                print(f"  Занято мест: {schedule.booked}")
            elif choice == "10":
                schedule = cancel_schedule(schedules,
                                           input_int("  Id занятия: ", minimum=1))
                print(f"  {schedule.status_text}")
            elif choice == "11":
                schedule = mark_schedule_done(schedules,
                                              input_int("  Id занятия: ", minimum=1))
                print(f"  Занятие № {schedule.id} отмечено проведённым.")
            else:
                print("  Такого пункта нет.")
        except GuideServiceError as error:
            print(f"\n  Ошибка: {error}")
        except ValueError as error:
            print(f"\n  Ошибка ввода: {error}")


# --- меню статистики ------------------------------------------------------

def statistics_menu(schedules, excursions, guides, routes):
    """Меню статистики."""
    while True:
        print_header("СТАТИСТИКА")
        print("  1. Сводные показатели")
        print("  2. Загрузка гидов")
        print("  3. Популярность маршрутов")
        print("  4. Выручка по экскурсиям")
        print("  5. Заполняемость занятий")
        print("  6. Активность по дням недели")
        print("  0. Назад")
        try:
            choice = input("  Выберите действие: ").strip()
            if choice == "0":
                return
            elif choice == "1":
                summary = build_summary(schedules)
                print(f"\n  Всего занятий: {summary['total']}")
                print(f"  Проведено: {summary['done']}")
                print(f"  Отменено: {summary['cancelled']}")
                print(f"  Участников: {summary['participants']}")
                print(f"  Выручка: {summary['revenue']} рублей")
                print(f"\n  {summary_line(summary)}")
            elif choice == "2":
                rows = count_schedules_by_guide(schedules, guides)
                print_table(("Гид", "Занятий"), rows)
            elif choice == "3":
                rows = count_schedules_by_route(schedules, routes)
                print_table(("Маршрут", "Занятий"), rows)
            elif choice == "4":
                rows = []
                for excursion in excursions:
                    money = 0
                    for item in schedules:
                        if item.excursion.id == excursion.id:
                            money += item.revenue
                    rows.append((excursion.title, round(money, 2)))
                print_table(("Экскурсия", "Выручка"), rows)
                print(f"\n  Итого: {total_revenue(schedules)} рублей")
            elif choice == "5":
                print_table(("Дата и время", "Мест", "Занято", "Свободно"),
                            occupancy_report(schedules))
            elif choice == "6":
                print_table(("День недели", "Занятий"), weekday_activity(schedules))
            else:
                print("  Такого пункта нет.")
        except GuideServiceError as error:
            print(f"\n  Ошибка: {error}")
        except ValueError as error:
            print(f"\n  Ошибка ввода: {error}")


# --- сценарии из ПР1 ------------------------------------------------------

def pr1_guide_scenario(schedules, excursions, guides):
    """Сценарий ПР1: свободен ли гид на выбранную дату.

    В ПР1 здесь были отдельные переменные, в ПР2 словари, теперь объекты.
    """
    if not guides or not excursions:
        print("  Нужны хотя бы один гид и одна экскурсия.")
        return

    show_guides(guides, "Гиды")
    guide = get_guide(guides, input_int("  Id гида: ", minimum=1))

    show_excursions(excursions, "Экскурсии")
    excursion = get_excursion(excursions, input_int("  Id экскурсии: ", minimum=1))

    schedule_date = input_date("  Дата проверки (ДД.ММ.ГГГГ): ")

    # если занятие уже стоит в расписании, берём его время, иначе 10:00
    start_time = "10:00"
    planned = find_schedule(schedules, excursion_id=excursion.id,
                            guide_id=guide.id, schedule_date=schedule_date)
    if planned is not None:
        start_time = planned.start_time

    conflicts = find_guide_conflicts(schedules, guide, schedule_date, start_time)
    languages_ok = guide.knows_languages(excursion.route.required_languages)

    print("\n  Результат проверки:")
    print(f"  Гид: {guide}")
    print(f"  Экскурсия: {excursion}")
    print(f"  Маршрут: {excursion.route}")
    print(f"  Дата и время: {format_date(schedule_date)} {start_time}")
    print(f"  Языки маршрута: {'подходят' if languages_ok else 'не подходят'}")
    print(f"  Статус: {guide.get_status(is_busy=bool(conflicts))}")


def pr1_excursion_scenario(schedules, excursions):
    """Сценарий ПР1: можно ли провести экскурсию на дату."""
    if not excursions:
        print("  Список экскурсий пуст.")
        return

    show_excursions(excursions, "Экскурсии")
    excursion = get_excursion(excursions, input_int("  Id экскурсии: ", minimum=1))
    schedule_date = input_date("  Дата (ДД.ММ.ГГГГ): ")

    relevant = []
    for item in filter_schedules_by_date(schedules, schedule_date):
        if item.excursion.id == excursion.id and not item.is_cancelled:
            relevant.append(item)

    is_available = True
    if relevant:
        is_available = False
        for item in relevant:
            if item.free_seats > 0:
                is_available = True

    print("\n  Результат проверки:")
    print(f"  Экскурсия: {excursion}")
    print(f"  Дата: {format_date(schedule_date)}")
    print(f"  Статус: {excursion.get_status(is_available)}")
    if relevant:
        for item in relevant:
            print(f"    Занятие № {item.id}: {item.start_time}, "
                  f"свободно {item.free_seats} мест")
    else:
        print("  Занятий на эту дату нет, экскурсию можно назначить.")


# --- запуск ---------------------------------------------------------------

MENU_ITEMS = (
    ("1", "Гиды"),
    ("2", "Маршруты"),
    ("3", "Экскурсии"),
    ("4", "Расписание"),
    ("5", "Статистика"),
    ("6", "Сохранить данные"),
    ("7", "Проверить, свободен ли гид (сценарий ПР1)"),
    ("8", "Проверить экскурсию на дату (сценарий ПР1)"),
    ("0", "Выход"),
)


def print_menu():
    """Напечатать главное меню."""
    print_header("СЕРВИС УПРАВЛЕНИЯ ТУРИСТИЧЕСКИМИ ГИДАМИ")
    for key, text in MENU_ITEMS:
        print(f"  {key}. {text}")


def main():
    """Загрузить данные, показать меню, сохранить изменения."""
    print_header("СЕРВИС УПРАВЛЕНИЯ ТУРИСТИЧЕСКИМИ ГИДАМИ")
    print("Программа для учёта гидов, маршрутов, экскурсий и расписания.")

    try:
        guides, routes, excursions, schedules = load_all()
    except StorageError as error:
        print(f"  Не удалось загрузить данные: {error}")
        guides, routes, excursions, schedules = [], [], [], []

    print(f"\n  Загружено: гидов {len(guides)}, маршрутов {len(routes)}, "
          f"экскурсий {len(excursions)}, занятий {len(schedules)}")

    while True:
        print_menu()
        try:
            choice = input("  Выберите действие: ").strip()
            if choice == "0":
                if input_yes_no("  Сохранить изменения?"):
                    save_all(guides, routes, excursions, schedules)
                    print("  Данные сохранены.")
                print("\n  Работа завершена.")
                return
            elif choice == "1":
                guides_menu(guides)
            elif choice == "2":
                routes_menu(routes, excursions)
            elif choice == "3":
                excursions_menu(excursions, routes, schedules)
            elif choice == "4":
                schedules_menu(schedules, excursions, guides, routes)
            elif choice == "5":
                statistics_menu(schedules, excursions, guides, routes)
            elif choice == "6":
                counts = save_all(guides, routes, excursions, schedules)
                print(f"  Сохранено: {counts}")
            elif choice == "7":
                pr1_guide_scenario(schedules, excursions, guides)
            elif choice == "8":
                pr1_excursion_scenario(schedules, excursions)
            else:
                print("  Такого пункта нет.")
        except GuideServiceError as error:
            print(f"\n  Ошибка: {error}")
        except ValueError as error:
            print(f"\n  Ошибка ввода: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\n  Ввод прерван, сохраняю данные.")
            save_all(guides, routes, excursions, schedules)
            return


if __name__ == "__main__":
    main()
