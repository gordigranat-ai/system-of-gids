"""Модель экскурсии."""

from decimal import Decimal

from django.db import models

from routes.models import Route

KINDS = (
    ("обычная экскурсия", "обычная экскурсия"),
    ("семейная экскурсия", "семейная экскурсия"),
)

GROUP_DISCOUNT = Decimal("0.1")
GROUP_SIZE_FOR_DISCOUNT = 6
CHILD_DISCOUNT = Decimal("0.5")


class Excursion(models.Model):
    """Экскурсия, которая проводится по маршруту."""

    title = models.CharField(
        max_length=200,
        verbose_name="Название экскурсии",
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.PROTECT,
        related_name="excursions",
        verbose_name="Маршрут",
    )
    kind = models.CharField(
        max_length=50,
        choices=KINDS,
        default="обычная экскурсия",
        verbose_name="Вид экскурсии",
    )
    base_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Цена за человека, ₽",
    )
    max_participants = models.PositiveIntegerField(
        verbose_name="Максимум участников",
    )
    min_age = models.PositiveIntegerField(
        default=0,
        verbose_name="Минимальный возраст",
    )
    languages = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Языки",
        help_text="Перечислите языки через запятую",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Экскурсия действует",
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "Экскурсия"
        verbose_name_plural = "Экскурсии"

    def __str__(self):
        return f"{self.title} ({self.route.name})"

    @property
    def duration_hours(self):
        """Продолжительность берётся у маршрута."""
        return self.route.duration_hours

    @property
    def is_family(self):
        return self.kind == "семейная экскурсия"

    @property
    def languages_list(self):
        return [item.strip() for item in self.languages.split(",") if item.strip()]

    def is_suitable_for(self, group_size):
        """Помещается ли группа на экскурсию."""
        return 0 < group_size <= self.max_participants

    def price_per_person(self, participant_age=18):
        """Цена за человека с учётом детской скидки."""
        if self.is_family and participant_age < 18:
            return self.base_price * CHILD_DISCOUNT
        return self.base_price

    def total_price(self, group_size, participant_age=18):
        """Стоимость экскурсии для группы."""
        if not self.is_suitable_for(group_size):
            raise ValueError(
                f"Группа {group_size} человек не подходит: "
                f"мест всего {self.max_participants}"
            )

        total = self.price_per_person(participant_age) * group_size
        if group_size >= GROUP_SIZE_FOR_DISCOUNT:
            total = total * (1 - GROUP_DISCOUNT)
        return round(total, 2)
