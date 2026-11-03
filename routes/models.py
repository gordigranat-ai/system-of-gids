"""Модель маршрута экскурсии."""

from django.db import models

DIFFICULTIES = (
    ("лёгкий", "лёгкий"),
    ("средний", "средний"),
    ("сложный", "сложный"),
)


class Route(models.Model):
    """Маршрут, по которому проводятся экскурсии."""

    name = models.CharField(
        max_length=200,
        verbose_name="Название маршрута",
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
