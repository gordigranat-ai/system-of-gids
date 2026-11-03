"""Модель занятия в расписании.

Занятие связывает экскурсию и гида: это две связи «многие к одному».
"""

from django.db import models
from django.db.models import Q

from excursions.models import Excursion
from guides.models import Guide

STATUS_PLANNED = "запланирована"
STATUS_DONE = "проведена"
STATUS_CANCELLED = "отменена"

STATUS_CHOICES = (
    (STATUS_PLANNED, "запланирована"),
    (STATUS_DONE, "проведена"),
    (STATUS_CANCELLED, "отменена"),
)


class Schedule(models.Model):
    """Занятие: какая экскурсия, какой гид, когда и сколько мест занято."""

    excursion = models.ForeignKey(
        Excursion,
        on_delete=models.PROTECT,
        related_name="schedules",
        verbose_name="Экскурсия",
    )
    guide = models.ForeignKey(
        Guide,
        on_delete=models.PROTECT,
        related_name="schedules",
        verbose_name="Гид",
    )
    date = models.DateField(
        verbose_name="Дата",
    )
    start_time = models.TimeField(
        verbose_name="Время начала",
    )
    booked = models.PositiveIntegerField(
        default=0,
        verbose_name="Забронировано мест",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PLANNED,
        verbose_name="Статус",
    )
    note = models.TextField(
        blank=True,
        verbose_name="Примечание",
    )

    class Meta:
        ordering = ["date", "start_time"]
        verbose_name = "Занятие"
        verbose_name_plural = "Расписание"
        constraints = [
            models.CheckConstraint(
                condition=Q(booked__gte=0),
                name="schedule_booked_not_negative",
            ),
        ]
        indexes = [
            models.Index(fields=["date"], name="schedule_date_idx"),
        ]

    def __str__(self):
        return (
            f"{self.date} {self.start_time:%H:%M}: {self.excursion.title}, "
            f"гид — {self.guide.name}"
        )

    @property
    def free_seats(self):
        """Сколько мест свободно."""
        return self.excursion.max_participants - self.booked

    @property
    def revenue(self):
        """Выручка занятия."""
        return round(self.excursion.base_price * self.booked, 2)

    @property
    def fill_percent(self):
        """Заполняемость занятия в процентах."""
        capacity = self.excursion.max_participants
        if capacity <= 0:
            return 0
        return round(self.booked * 100 / capacity)

    @property
    def is_cancelled(self):
        return self.status == STATUS_CANCELLED

    def cancel(self):
        """Отменить занятие, не удаляя его из истории."""
        self.status = STATUS_CANCELLED
        self.save(update_fields=["status"])

    def mark_done(self):
        """Отметить занятие проведённым."""
        self.status = STATUS_DONE
        self.save(update_fields=["status"])
