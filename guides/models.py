"""Модель гида.

Это Django-модель (ПР9), а не класс предметной области из корневого
models.py: она описывает таблицу базы и даёт доступ к данным через ORM.
"""

from django.db import models


class Guide(models.Model):
    """Гид экскурсионного бюро."""

    name = models.CharField(
        max_length=200,
        verbose_name="Имя гида",
    )
    specialization = models.CharField(
        max_length=100,
        verbose_name="Специализация",
    )
    languages = models.CharField(
        max_length=200,
        verbose_name="Языки",
        help_text="Перечислите языки через запятую",
    )
    experience_years = models.PositiveIntegerField(
        default=0,
        verbose_name="Стаж, лет",
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0,
        verbose_name="Рейтинг",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Работает с экскурсиями",
    )
    photo = models.ImageField(
        upload_to="guides/",
        blank=True,
        verbose_name="Фотография",
        help_text="Необязательно. JPG или PNG, не больше 2 МБ",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Гид"
        verbose_name_plural = "Гиды"

    def __str__(self):
        return self.name

    @property
    def languages_list(self):
        """Языки списком — для шаблонов и проверок."""
        return [item.strip() for item in self.languages.split(",") if item.strip()]

    def knows_languages(self, required_languages):
        """Знает ли гид все требуемые языки."""
        mine = {item.lower() for item in self.languages_list}
        return all(str(item).lower() in mine for item in required_languages)
