"""Классы и функции предметной области.

Классы: Guide (гид), Route (маршрут), Excursion (экскурсия),
FamilyExcursion (семейная, детям скидка), Schedule (занятие в расписании).

Ниже — функции работы со списками объектов: поиск, отбор, сортировка,
добавление. Они остались функциями, потому что относятся к списку,
а не к одному объекту.

В начале файла свои исключения: в меню достаточно поймать GuideServiceError
и показать сообщение.
"""

from datetime import date


# --- исключения -----------------------------------------------------------

class GuideServiceError(Exception):
    """Общая ошибка проекта."""


class ValidationError(GuideServiceError):
    """Данные не прошли проверку."""


class NotFoundError(GuideServiceError):
    """Запись с таким id не найдена."""


class DuplicateError(GuideServiceError):
    """Такая запись уже есть."""


class BusyGuideError(GuideServiceError):
    """Гид уже занят в это время."""


class CapacityError(GuideServiceError):
    """Участников больше, чем мест."""


class StorageError(GuideServiceError):
    """Ошибка чтения или записи файла."""


# --- константы ------------------------------------------------------------

SPECIALIZATIONS = (
    "городская экскурсия",
    "музейная экскурсия",
    "природная экскурсия",
    "гастрономическая экскурсия",
    "детская экскурсия",
)

DIFFICULTIES = ("лёгкий", "средний", "сложный")

STATUS_SCHEDULED = "запланирована"
STATUS_DONE = "проведена"
STATUS_CANCELLED = "отменена"

GROUP_DISCOUNT = 0.1           # скидка группе от 6 человек
GROUP_SIZE_FOR_DISCOUNT = 6


# --- классы ---------------------------------------------------------------

class Guide:
    """Гид."""

    def __init__(self, guide_id, name, specialization, languages,
                 experience_years=0, rating=0.0, is_active=True):
        self.id = guide_id
        self.name = name
        self.specialization = specialization
        self.languages = list(languages)
        self.experience_years = experience_years
        self.rating = rating
        self.is_active = is_active

    def knows_languages(self, required_languages):
        """Знает ли гид все нужные языки."""
        mine = [language.lower() for language in self.languages]
        return all(str(item).lower() in mine for item in required_languages)

    def get_status(self, is_busy=False):
        """Текстовый статус гида (метод из сценария ПР1)."""
        if not self.is_active:
            return "Гид не работает с экскурсиями"
        if is_busy:
            return "Гид занят в указанное время"
        return "Гид свободен и может провести экскурсию"

    def set_active(self, is_active):
        self.is_active = is_active

    @staticmethod
    def validate_languages(languages):
        """Есть ли в списке хотя бы один язык."""
        return any(str(item).strip() for item in languages)

    @classmethod
    def from_data(cls, data):
        """Создать гида из данных файла."""
        return cls(
            guide_id=data.get("id"),
            name=str(data.get("name", "")).strip(),
            specialization=str(data.get("specialization", "")).strip(),
            languages=data.get("languages", []),
            experience_years=data.get("experience_years", 0),
            rating=data.get("rating", 0),
            is_active=data.get("is_active", True),
        )

    def attributes(self):
        """Данные гида словарём — для сохранения в файл."""
        return {
            "id": self.id,
            "name": self.name,
            "specialization": self.specialization,
            "languages": list(self.languages),
            "experience_years": self.experience_years,
            "rating": self.rating,
            "is_active": self.is_active,
        }

    def __str__(self):
        return f"{self.name} ({self.specialization}, языки: {', '.join(self.languages)})"


class Route:
    """Маршрут экскурсии."""

    def __init__(self, route_id, name, duration_hours, difficulty, description="",
                 distance_km=0.0, required_languages=None, is_active=True):
        self.id = route_id
        self.name = name
        self.duration_hours = duration_hours
        self.difficulty = difficulty
        self.description = description
        self.distance_km = distance_km
        self.required_languages = list(required_languages or [])
        self.is_active = is_active

    def is_suitable_duration(self, max_hours):
        """Укладывается ли маршрут в отведённое время."""
        return self.duration_hours <= max_hours

    @staticmethod
    def validate_difficulty(difficulty):
        """Входит ли сложность в список допустимых."""
        return difficulty in DIFFICULTIES

    @classmethod
    def from_data(cls, data):
        """Создать маршрут из данных файла."""
        return cls(
            route_id=data.get("id"),
            name=str(data.get("name", "")).strip(),
            duration_hours=data.get("duration_hours", 0),
            difficulty=data.get("difficulty", "лёгкий"),
            description=str(data.get("description", "")),
            distance_km=data.get("distance_km", 0),
            required_languages=data.get("required_languages", []),
            is_active=data.get("is_active", True),
        )

    def attributes(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "duration_hours": self.duration_hours,
            "distance_km": self.distance_km,
            "difficulty": self.difficulty,
            "required_languages": list(self.required_languages),
            "is_active": self.is_active,
        }

    def __str__(self):
        return f"{self.name} ({self.duration_hours} ч, {self.difficulty})"


class Excursion:
    """Экскурсия, которая проводится по маршруту."""

    def __init__(self, excursion_id, title, route, max_participants, base_price,
                 languages=None, min_age=0, is_active=True):
        self.id = excursion_id
        self.title = title
        self.route = route
        self.max_participants = max_participants
        self.base_price = base_price
        self.languages = list(languages or route.required_languages)
        self.min_age = min_age
        self.is_active = is_active

    @property
    def kind(self):
        """Вид экскурсии."""
        return "обычная экскурсия"

    @property
    def duration_hours(self):
        """Продолжительность берём у маршрута."""
        return self.route.duration_hours

    def is_suitable_for(self, group_size):
        """Помещается ли группа на экскурсию."""
        return 0 < group_size <= self.max_participants

    def price_per_person(self, participant_age=18):
        """Цена за человека."""
        return self.base_price

    def total_price(self, group_size, participant_age=18):
        """Стоимость для группы, с групповой скидкой."""
        if group_size <= 0:
            raise ValidationError("Количество участников должно быть положительным")
        if not self.is_suitable_for(group_size):
            raise CapacityError(
                f"Экскурсия вмещает не более {self.max_participants} участников, "
                f"запрошено {group_size}"
            )
        total = self.price_per_person(participant_age) * group_size
        if group_size >= GROUP_SIZE_FOR_DISCOUNT:
            total = total * (1 - GROUP_DISCOUNT)
        return round(total, 2)

    def get_status(self, is_available=True):
        """Текстовый статус экскурсии."""
        if not self.is_active:
            return "Экскурсия снята с проведения"
        if not is_available:
            return "Экскурсия недоступна"
        return "Экскурсия доступна для бронирования"

    @classmethod
    def from_data(cls, data, route):
        """Создать экскурсию по данным файла и связать её с маршрутом."""
        return cls(
            excursion_id=data.get("id"),
            title=str(data.get("title", "")).strip(),
            route=route,
            max_participants=data.get("max_participants", 0),
            base_price=data.get("base_price", 0),
            languages=data.get("languages", []),
            min_age=data.get("min_age", 0),
            is_active=data.get("is_active", True),
        )

    def attributes(self):
        """Данные экскурсии: вместо объекта маршрута пишем его id."""
        return {
            "id": self.id,
            "title": self.title,
            "route_id": self.route.id,
            "kind": self.kind,
            "base_price": self.base_price,
            "max_participants": self.max_participants,
            "min_age": self.min_age,
            "languages": list(self.languages),
            "is_active": self.is_active,
        }

    def __str__(self):
        return (f"{self.title} ({self.kind}, маршрут «{self.route.name}», "
                f"{self.max_participants} мест, {self.base_price} руб.)")


class FamilyExcursion(Excursion):
    """Семейная экскурсия: детям до 12 лет цена со скидкой 50 %."""

    @property
    def kind(self):
        return "семейная экскурсия"

    def price_per_person(self, participant_age=18):
        """Детям считаем половину цены, взрослым — полную."""
        if participant_age < 12:
            return self.base_price * 0.5
        return self.base_price

    def __str__(self):
        return f"{super().__str__()} — детям скидка 50 %"


# какие виды экскурсий бывают — нужно при загрузке из файла
EXCURSION_CLASSES = {
    "обычная экскурсия": Excursion,
    "семейная экскурсия": FamilyExcursion,
}


class Schedule:
    """Занятие в расписании: экскурсия, гид, дата и время."""

    def __init__(self, schedule_id, excursion, guide, schedule_date, start_time,
                 booked=0, status=STATUS_SCHEDULED, note=""):
        self.id = schedule_id
        self.excursion = excursion
        self.guide = guide
        self.schedule_date = schedule_date
        self.start_time = start_time
        self.booked = booked
        self.status = status
        self.note = note

    @property
    def date(self):
        """Дата строкой — так её удобно сравнивать."""
        return self.schedule_date.strftime("%Y-%m-%d")

    @property
    def route(self):
        """Маршрут экскурсии."""
        return self.excursion.route

    @property
    def free_seats(self):
        """Сколько мест свободно."""
        return self.excursion.max_participants - self.booked

    @property
    def revenue(self):
        """Выручка занятия."""
        return round(self.excursion.base_price * self.booked, 2)

    @property
    def is_cancelled(self):
        return self.status == STATUS_CANCELLED

    @property
    def status_text(self):
        """Текст про состояние занятия."""
        if self.is_cancelled:
            return "Занятие отменено"
        if self.status == STATUS_DONE:
            return "Занятие проведено"
        return "Занятие запланировано"

    def get_time_range(self):
        """Время занятия в минутах: начало и конец."""
        hours, minutes = self.start_time.split(":")
        start = int(hours) * 60 + int(minutes)
        end = start + int(self.excursion.duration_hours * 60)
        return start, end

    def is_overlapped_with(self, other):
        """Пересекается ли занятие с другим занятием того же гида."""
        if self.guide.id != other.guide.id or self.date != other.date:
            return False
        if self.is_cancelled or other.is_cancelled:
            return False
        start, end = self.get_time_range()
        other_start, other_end = other.get_time_range()
        return start < other_end and other_start < end

    def book_seats(self, group_size):
        """Забронировать места."""
        if self.is_cancelled:
            raise ValidationError("Нельзя бронировать отменённое занятие")
        if group_size <= 0:
            raise ValidationError("Количество участников должно быть положительным")
        if group_size > self.free_seats:
            raise CapacityError(f"Свободно только {self.free_seats} мест, "
                                f"запрошено {group_size}")
        self.booked = self.booked + group_size
        return self.booked

    def cancel_seats(self, group_size):
        """Отменить часть брони."""
        if group_size > self.booked:
            raise ValidationError(f"Забронировано только {self.booked} мест")
        self.booked = self.booked - group_size
        return self.booked

    def cancel(self):
        """Отменить занятие: объект остаётся, меняется статус."""
        self.status = STATUS_CANCELLED

    def mark_done(self):
        """Отметить занятие проведённым."""
        if self.is_cancelled:
            raise ValidationError("Отменённое занятие нельзя отметить проведённым")
        self.status = STATUS_DONE

    @classmethod
    def from_data(cls, data, excursion, guide):
        """Создать занятие из данных файла."""
        year, month, day = str(data.get("date", "")).split("-")
        return cls(
            schedule_id=data.get("id"),
            excursion=excursion,
            guide=guide,
            schedule_date=date(int(year), int(month), int(day)),
            start_time=str(data.get("start_time", "00:00")),
            booked=data.get("booked", 0),
            status=data.get("status", STATUS_SCHEDULED),
            note=str(data.get("note", "")),
        )

    def attributes(self):
        """Данные занятия: вместо объектов пишем их id."""
        return {
            "id": self.id,
            "excursion_id": self.excursion.id,
            "guide_id": self.guide.id,
            "date": self.date,
            "start_time": self.start_time,
            "booked": self.booked,
            "status": self.status,
            "note": self.note,
        }

    def __str__(self):
        return (f"{self.date} {self.start_time}: {self.excursion.title}, "
                f"гид - {self.guide.name}, {self.booked} из "
                f"{self.excursion.max_participants} мест")


# --- функции работы со списком гидов -------------------------------------

def add_guide(guides, guide):
    """Добавить гида в список."""
    if not guide.name:
        raise ValidationError("Имя гида не может быть пустым")
    if guide.specialization not in SPECIALIZATIONS:
        raise ValidationError("Такой специализации нет в справочнике")
    if not Guide.validate_languages(guide.languages):
        raise ValidationError("Нужно указать хотя бы один язык")
    if find_guide_by_name(guides, guide.name) is not None:
        raise DuplicateError(f"Гид '{guide.name}' уже есть в справочнике")

    guides.append(guide)
    return guide


def create_guide(guides, name, specialization, languages, experience_years=0,
                 rating=0.0):
    """Создать гида с новым id."""
    guide = Guide(len(guides) + 1, name, specialization, languages,
                  experience_years, rating)
    return add_guide(guides, guide)


def get_guide(guides, guide_id):
    """Найти гида по id или возбудить NotFoundError."""
    for guide in guides:
        if guide.id == guide_id:
            return guide
    raise NotFoundError(f"Гид с идентификатором {guide_id} не найден")


def find_guide_by_name(guides, name):
    """Найти гида по имени."""
    for guide in guides:
        if guide.name.lower() == name.lower():
            return guide
    return None


def search_guides(guides, query):
    """Гиды, в имени которых есть подстрока."""
    return [guide for guide in guides if query.lower() in guide.name.lower()]


def filter_guides_by_language(guides, language):
    """Гиды, которые знают язык."""
    return [guide for guide in guides if guide.knows_languages([language])]


def filter_guides_by_specialization(guides, specialization):
    """Гиды с указанной специализацией."""
    return [guide for guide in guides if guide.specialization == specialization]


def filter_guides_by_experience(guides, min_experience):
    """Гиды со стажем не меньше указанного."""
    return [guide for guide in guides if guide.experience_years >= min_experience]


def sort_guides(guides, field="рейтинг", reverse=True):
    """Отсортировать гидов по имени, стажу или рейтингу."""
    if field == "имя":
        return sorted(guides, key=lambda guide: guide.name, reverse=reverse)
    if field == "стаж":
        return sorted(guides, key=lambda guide: guide.experience_years,
                      reverse=reverse)
    if field == "рейтинг":
        return sorted(guides, key=lambda guide: guide.rating, reverse=reverse)
    raise ValidationError(f"Нельзя сортировать по полю '{field}'")


def remove_guide(guides, guide_id):
    """Удалить гида."""
    guide = get_guide(guides, guide_id)
    guides.remove(guide)
    return guide


# --- функции работы со списком маршрутов ----------------------------------

def add_route(routes, route):
    """Добавить маршрут в список."""
    if not route.name:
        raise ValidationError("Название маршрута не может быть пустым")
    if route.duration_hours <= 0:
        raise ValidationError("Продолжительность должна быть больше нуля")
    if not Route.validate_difficulty(route.difficulty):
        raise ValidationError("Такой сложности нет в справочнике")
    if find_route_by_name(routes, route.name) is not None:
        raise DuplicateError(f"Маршрут '{route.name}' уже есть в справочнике")

    routes.append(route)
    return route


def create_route(routes, name, duration_hours, difficulty, description="",
                 distance_km=0.0, required_languages=None):
    """Создать маршрут с новым id."""
    route = Route(len(routes) + 1, name, duration_hours, difficulty, description,
                  distance_km, required_languages)
    return add_route(routes, route)


def get_route(routes, route_id):
    """Найти маршрут по id или возбудить NotFoundError."""
    for route in routes:
        if route.id == route_id:
            return route
    raise NotFoundError(f"Маршрут с идентификатором {route_id} не найден")


def find_route_by_name(routes, name):
    """Найти маршрут по названию."""
    for route in routes:
        if route.name.lower() == name.lower():
            return route
    return None


def search_routes(routes, query):
    """Маршруты, у которых подстрока есть в названии или описании."""
    text = query.lower()
    return [route for route in routes
            if text in route.name.lower() or text in route.description.lower()]


def filter_routes_by_difficulty(routes, difficulty):
    """Маршруты указанной сложности."""
    return [route for route in routes if route.difficulty == difficulty]


def filter_routes_by_duration(routes, max_duration):
    """Маршруты, которые укладываются в указанное время."""
    return [route for route in routes if route.is_suitable_duration(max_duration)]


def sort_routes(routes, field="длительность"):
    """Отсортировать маршруты по названию или длительности."""
    if field == "название":
        return sorted(routes, key=lambda route: route.name)
    if field == "длительность":
        return sorted(routes, key=lambda route: route.duration_hours)
    raise ValidationError(f"Нельзя сортировать по полю '{field}'")


def remove_route(routes, route_id):
    """Удалить маршрут."""
    route = get_route(routes, route_id)
    routes.remove(route)
    return route


# --- функции работы со списком экскурсий ----------------------------------

def add_excursion(excursions, excursion):
    """Добавить экскурсию в список."""
    if not excursion.title:
        raise ValidationError("Название экскурсии не может быть пустым")
    if excursion.base_price <= 0:
        raise ValidationError("Стоимость должна быть больше нуля")
    if excursion.max_participants <= 0:
        raise ValidationError("Количество участников должно быть положительным")
    if find_excursion_by_title(excursions, excursion.title) is not None:
        raise DuplicateError(f"Экскурсия '{excursion.title}' уже есть в справочнике")

    excursions.append(excursion)
    return excursion


def create_excursion(excursions, title, route, base_price, max_participants,
                     languages=None, min_age=0, family=False):
    """Создать экскурсию. Если family=True — семейную, с детской скидкой."""
    excursion_class = FamilyExcursion if family else Excursion
    excursion = excursion_class(len(excursions) + 1, title, route,
                                max_participants, base_price, languages, min_age)
    return add_excursion(excursions, excursion)


def get_excursion(excursions, excursion_id):
    """Найти экскурсию по id или возбудить NotFoundError."""
    for excursion in excursions:
        if excursion.id == excursion_id:
            return excursion
    raise NotFoundError(f"Экскурсия с идентификатором {excursion_id} не найдена")


def find_excursion_by_title(excursions, title):
    """Найти экскурсию по названию."""
    for excursion in excursions:
        if excursion.title.lower() == title.lower():
            return excursion
    return None


def search_excursions(excursions, query):
    """Экскурсии, в названии которых есть подстрока."""
    return [item for item in excursions if query.lower() in item.title.lower()]


def filter_excursions_by_price(excursions, max_price):
    """Экскурсии не дороже указанной суммы."""
    return [item for item in excursions if item.base_price <= max_price]


def filter_excursions_by_route(excursions, route_id):
    """Экскурсии по конкретному маршруту."""
    return [item for item in excursions if item.route.id == route_id]


def filter_excursions_for_group(excursions, group_size):
    """Экскурсии, которые вмещают такую группу."""
    return [item for item in excursions if item.is_suitable_for(group_size)]


def filter_excursions_for_children(excursions):
    """Экскурсии, подходящие детям."""
    return [item for item in excursions if item.min_age <= 6]


def sort_excursions(excursions, field="цена"):
    """Отсортировать экскурсии по названию или цене."""
    if field == "название":
        return sorted(excursions, key=lambda item: item.title)
    if field == "цена":
        return sorted(excursions, key=lambda item: item.base_price)
    raise ValidationError(f"Нельзя сортировать по полю '{field}'")


def remove_excursion(excursions, excursion_id):
    """Удалить экскурсию."""
    excursion = get_excursion(excursions, excursion_id)
    excursions.remove(excursion)
    return excursion


# --- функции работы с расписанием -----------------------------------------

def add_schedule(schedules, schedule):
    """Добавить занятие, проверив гида, языки и пересечения по времени."""
    if not schedule.excursion.is_active:
        raise ValidationError("Экскурсия снята с проведения")
    if not schedule.guide.is_active:
        raise ValidationError(f"Гид '{schedule.guide.name}' не работает")

    languages = schedule.route.required_languages
    if not schedule.guide.knows_languages(languages):
        raise ValidationError(f"Гид не знает языки маршрута: {', '.join(languages)}")

    for item in schedules:
        if (item.excursion.id == schedule.excursion.id
                and item.guide.id == schedule.guide.id
                and item.date == schedule.date
                and item.start_time == schedule.start_time):
            raise DuplicateError("Такое занятие уже есть в расписании")
        if item.is_overlapped_with(schedule):
            raise BusyGuideError(f"Гид занят {schedule.date} в {item.start_time} "
                                 f"(занятие № {item.id})")

    schedules.append(schedule)
    return schedule


def create_schedule(schedules, excursion, guide, schedule_date, start_time, note=""):
    """Создать занятие с новым id и добавить его в расписание."""
    schedule = Schedule(len(schedules) + 1, excursion, guide, schedule_date,
                        start_time, note=note)
    return add_schedule(schedules, schedule)


def get_schedule(schedules, schedule_id):
    """Найти занятие по id или возбудить NotFoundError."""
    for schedule in schedules:
        if schedule.id == schedule_id:
            return schedule
    raise NotFoundError(f"Занятие с идентификатором {schedule_id} не найдено")


def find_schedule(schedules, excursion_id=None, guide_id=None,
                  schedule_date=None, start_time=None):
    """Поиск занятия по условиям. Что не указано, то не проверяем."""
    for item in schedules:
        if excursion_id is not None and item.excursion.id != excursion_id:
            continue
        if guide_id is not None and item.guide.id != guide_id:
            continue
        if schedule_date is not None and item.date != schedule_date.strftime("%Y-%m-%d"):
            continue
        if start_time is not None and item.start_time != start_time:
            continue
        return item
    return None


def find_guide_conflicts(schedules, guide, schedule_date, start_time):
    """Занятия гида, которые пересекаются с указанным временем.

    Отменённые занятия не считаем: они время гида не занимают.
    """
    hours, minutes = start_time.split(":")
    start = int(hours) * 60 + int(minutes)
    conflicts = []
    for item in schedules:
        if item.guide.id != guide.id or item.is_cancelled:
            continue
        if item.date != schedule_date.strftime("%Y-%m-%d"):
            continue
        item_start, item_end = item.get_time_range()
        if start < item_end and item_start < start + 60:
            conflicts.append(item)
    return conflicts


def is_guide_available(schedules, guide, schedule_date, start_time):
    """Свободен ли гид в это время."""
    return not find_guide_conflicts(schedules, guide, schedule_date, start_time)


def book_seats(schedules, schedule_id, group_size):
    """Забронировать места на занятии."""
    schedule = get_schedule(schedules, schedule_id)
    schedule.book_seats(group_size)
    return schedule


def cancel_seats(schedules, schedule_id, group_size):
    """Отменить часть брони."""
    schedule = get_schedule(schedules, schedule_id)
    schedule.cancel_seats(group_size)
    return schedule


def cancel_schedule(schedules, schedule_id):
    """Отменить занятие."""
    schedule = get_schedule(schedules, schedule_id)
    schedule.cancel()
    return schedule


def mark_schedule_done(schedules, schedule_id):
    """Отметить занятие проведённым."""
    schedule = get_schedule(schedules, schedule_id)
    schedule.mark_done()
    return schedule


def filter_schedules_by_date(schedules, schedule_date):
    """Занятия на дату."""
    target = schedule_date.strftime("%Y-%m-%d")
    return [item for item in schedules if item.date == target]


def filter_schedules_by_guide(schedules, guide_id):
    """Занятия гида."""
    return [item for item in schedules if item.guide.id == guide_id]


def filter_schedules_by_period(schedules, date_from, date_to):
    """Занятия за период."""
    start = date_from.strftime("%Y-%m-%d")
    end = date_to.strftime("%Y-%m-%d")
    return [item for item in schedules if start <= item.date <= end]


def filter_available_schedules(schedules):
    """Занятия, где ещё есть свободные места."""
    return [item for item in schedules
            if item.status == STATUS_SCHEDULED and item.free_seats > 0]
