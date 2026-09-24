"""Вспомогательные функции: ввод, даты, вывод таблиц."""

import functools
from datetime import datetime

DATE_FORMAT = "%d.%m.%Y"
TIME_FORMAT = "%H:%M"

WEEKDAYS = ("понедельник", "вторник", "среда", "четверг",
            "пятница", "суббота", "воскресенье")


def retry_on_error(description, attempts=3):
    """Декоратор: если функция возбудила ValueError, попробовать ещё раз.

    Так сделаны функции ввода: пользователь ошибся — его просят ввести
    значение заново, программа не падает.
    """

    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            for number in range(1, attempts + 1):
                try:
                    return function(*args, **kwargs)
                except ValueError as error:
                    if number == attempts:
                        raise
                    print(f"  Ошибка: {error}. Попробуйте ещё раз ({number} из {attempts}).")
            raise ValueError(f"Не удалось прочитать {description}")

        return wrapper

    return decorator


def read_line(prompt):
    """Прочитать строку и убрать пробелы по краям."""
    return input(prompt).strip()


def parse_date(value):
    """Строка с датой -> объект date. Понимаем ДД.ММ.ГГГГ и ГГГГ-ММ-ДД."""
    text = value.strip()
    for fmt in (DATE_FORMAT, "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Дата '{value}' не распознана, нужен формат ДД.ММ.ГГГГ")


def format_date(value):
    """Дата в виде ДД.ММ.ГГГГ."""
    return value.strftime(DATE_FORMAT)


def parse_time(value):
    """Проверить время ЧЧ:ММ."""
    text = value.strip()
    try:
        datetime.strptime(text, TIME_FORMAT)
    except ValueError:
        raise ValueError(f"Время '{value}' не распознано, нужен формат ЧЧ:ММ")
    return text


def time_to_minutes(value):
    """Время ЧЧ:ММ в минуты от начала суток."""
    hours, minutes = value.split(":")
    return int(hours) * 60 + int(minutes)


def weekday_title(value):
    """Название дня недели для даты."""
    return WEEKDAYS[value.weekday()]


@retry_on_error("целое число")
def input_int(prompt, minimum=None, maximum=None):
    """Прочитать целое число."""
    number = int(read_line(prompt))
    if minimum is not None and number < minimum:
        raise ValueError(f"значение не может быть меньше {minimum}")
    if maximum is not None and number > maximum:
        raise ValueError(f"значение не может быть больше {maximum}")
    return number


@retry_on_error("число")
def input_float(prompt, minimum=None, maximum=None):
    """Прочитать дробное число (запятую тоже принимаем)."""
    number = float(read_line(prompt).replace(",", "."))
    if minimum is not None and number < minimum:
        raise ValueError(f"значение не может быть меньше {minimum}")
    if maximum is not None and number > maximum:
        raise ValueError(f"значение не может быть больше {maximum}")
    return number


@retry_on_error("дату")
def input_date(prompt):
    """Прочитать дату."""
    return parse_date(read_line(prompt))


@retry_on_error("время")
def input_time(prompt):
    """Прочитать время."""
    return parse_time(read_line(prompt))


def input_choice(prompt, allowed):
    """Прочитать один из допустимых вариантов."""
    while True:
        answer = read_line(prompt)
        if answer in allowed:
            return answer
        print(f"  Допустимые варианты: {', '.join(allowed)}")


def input_yes_no(prompt, default=False):
    """Прочитать ответ да или нет."""
    suffix = " [Д/н]: " if default else " [д/Н]: "
    while True:
        answer = read_line(prompt + suffix).lower()
        if not answer:
            return default
        if answer in ("д", "да", "y", "yes"):
            return True
        if answer in ("н", "нет", "n", "no"):
            return False
        print("  Введите «д» или «н».")


def input_required(prompt):
    """Прочитать непустую строку."""
    while True:
        answer = read_line(prompt)
        if answer:
            return answer
        print("  Значение не может быть пустым.")


def split_list(value):
    """Строку «русский, английский» превратить в список."""
    return [item.strip() for item in value.split(",") if item.strip()]


def pluralize(number, forms):
    """Подобрать форму слова: 1 человек, 2 человека, 5 человек."""
    absolute = abs(number) % 100
    if 11 <= absolute <= 14:
        return forms[2]
    last = absolute % 10
    if last == 1:
        return forms[0]
    if 2 <= last <= 4:
        return forms[1]
    return forms[2]


def print_header(title, width=68):
    """Напечатать заголовок раздела."""
    print()
    print("=" * width)
    print(title)
    print("=" * width)


def print_table(headers, rows, empty_message="Данных нет."):
    """Напечатать таблицу, ширину столбцов считаем по содержимому."""
    if not rows:
        print(f"  {empty_message}")
        return

    widths = []
    for index in range(len(headers)):
        lengths = [len(str(headers[index]))]
        for row in rows:
            lengths.append(len(str(row[index])))
        widths.append(max(lengths))

    print("  ".join(str(headers[i]).ljust(widths[i]) for i in range(len(headers))))
    print("-" * (sum(widths) + 2 * (len(headers) - 1)))
    for row in rows:
        print("  ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))))


def show_guides(guides, title="Гиды"):
    """Напечатать таблицу гидов."""
    rows = [(guide.id, guide.name, guide.specialization,
             ", ".join(guide.languages), guide.experience_years, guide.rating)
            for guide in guides]
    print(f"\n{title}: {len(rows)} {pluralize(len(rows), ('запись', 'записи', 'записей'))}")
    print_table(("ID", "Имя", "Специализация", "Языки", "Стаж", "Рейтинг"), rows,
                "Гиды не найдены.")


def show_routes(routes, title="Маршруты"):
    """Напечатать таблицу маршрутов."""
    rows = [(route.id, route.name, route.duration_hours, route.distance_km,
             route.difficulty, ", ".join(route.required_languages))
            for route in routes]
    print(f"\n{title}: {len(rows)} {pluralize(len(rows), ('запись', 'записи', 'записей'))}")
    print_table(("ID", "Маршрут", "Часы", "Км", "Сложность", "Языки"), rows,
                "Маршруты не найдены.")


def show_excursions(excursions, title="Экскурсии"):
    """Напечатать таблицу экскурсий."""
    rows = [(item.id, item.title, item.kind, item.route.name, item.base_price,
             item.max_participants, item.min_age) for item in excursions]
    print(f"\n{title}: {len(rows)} {pluralize(len(rows), ('запись', 'записи', 'записей'))}")
    print_table(("ID", "Экскурсия", "Вид", "Маршрут", "Цена", "Мест", "Возраст"), rows,
                "Экскурсии не найдены.")


def show_schedules(schedules, title="Расписание"):
    """Напечатать таблицу занятий."""
    rows = [(item.id, format_date(item.schedule_date), item.start_time,
             item.excursion.title, item.guide.name,
             f"{item.booked} из {item.excursion.max_participants}", item.status)
            for item in schedules]
    print(f"\n{title}: {len(rows)} {pluralize(len(rows), ('запись', 'записи', 'записей'))}")
    print_table(("ID", "Дата", "Время", "Экскурсия", "Гид", "Мест", "Статус"), rows,
                "Занятия не найдены.")
