"""Модель маршрута экскурсии.

У маршрута есть человекочитаемый адрес (slug) и метод get_absolute_url(),
который строит ссылку на страницу маршрута по имени маршрута.
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

DIFFICULTIES = (
    ("лёгкий", "лёгкий"),
    ("средний", "средний"),
    ("сложный", "сложный"),
)

# Таблица транслитерации: slug маршрута должен состоять из латиницы.
TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e",
    "ё": "e", "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k",
    "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
    "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "",
    "э": "e", "ю": "yu", "я": "ya",
}


def transliterate(text):
    """Перевести кириллицу в латиницу для slug."""
    return "".join(TRANSLIT.get(char, char) for char in text.lower())


def make_slug(name, number=None):
    """Собрать slug из названия; number добавляется для уникальности."""
    base = slugify(transliterate(name)) or "route"
    if number is not None:
        return f"{base}-{number}"
    return base


class Route(models.Model):
    """Маршрут, по которому проводятся экскурсии."""

    name = models.CharField(
        max_length=200,
        verbose_name="Название маршрута",
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        verbose_name="Адрес страницы",
        help_text="Заполняется автоматически из названия",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    duration_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name="Продолжительность, ч",
    )
    distance_km = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=0,
        verbose_name="Протяжённость, км",
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTIES,
        default="лёгкий",
        verbose_name="Сложность",
    )
    required_languages = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Языки маршрута",
        help_text="Перечислите языки через запятую",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Маршрут действует",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"

    def __str__(self):
        return f"{self.name} ({self.duration_hours} ч, {self.difficulty})"

    def save(self, *args, **kwargs):
        """Заполнить slug из названия, если он не задан вручную."""
        if not self.slug:
            base = make_slug(self.name)
            candidate = base
            number = 2
            while Route.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = make_slug(self.name, number)
                number += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Ссылка на страницу маршрута по slug."""
        return reverse("routes:detail", args=[self.slug])

    @property
    def required_languages_list(self):
        """Языки маршрута списком — для шаблонов."""
        return [
            item.strip()
            for item in self.required_languages.split(",")
            if item.strip()
        ]

    def is_suitable_duration(self, max_hours):
        """Укладывается ли маршрут в отведённое время."""
        return self.duration_hours <= max_hours
