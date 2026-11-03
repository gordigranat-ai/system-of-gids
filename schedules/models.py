"""Модель занятия в расписании.

Занятие связывает экскурсию и гида. Статус описан через TextChoices:
в базе хранятся короткие латинские коды, а в интерфейсе показываются
русские подписи. Менеджер Schedule.objects даёт готовые методы выборки.
"""

from django.db import models
from django.db.models import Q, Sum

from excursions.models import Excursion
from guides.models import Guide


class ScheduleStatus(models.TextChoices):
    """Статус занятия: коды для базы и подписи для интерфейса."""

    ACTIVE = "active", "запланирована"
    COMPLETED = "completed", "проведена"
    CANCELLED = "cancelled", "отменена"


class ScheduleQuerySet(models.QuerySet):
    """Набор занятий с часто используемыми выборками."""

    def with_related(self):
        """Подтянуть экскурсию, её маршрут и гида одним запросом."""
        return self.select_related("excursion", "excursion__route", "guide")

    def active(self):
        """Занятия без отменённых."""
        return self.exclude(status=ScheduleStatus.CANCELLED)

    def completed(self):
        """Проведённые занятия."""
        return self.filter(status=ScheduleStatus.COMPLETED)

    def cancelled(self):
        """Отменённые занятия."""
        return self.filter(status=ScheduleStatus.CANCELLED)

    def for_guide(self, guide):
        """Занятия конкретного гида (объект или его идентификатор)."""
        guide_id = getattr(guide, "pk", guide)
        return self.filter(guide_id=guide_id)

    def on_date(self, day):
        """Занятия на указанную дату."""
        return self.filter(date=day)

    def busy_guides(self, day):
        """Гиды, у которых на дату есть неотменённое занятие."""
        return (
            self.on_date(day)
            .exclude(status=ScheduleStatus.CANCELLED)
            .values("guide_id")
        )

    def totals(self):
        """Итоги по набору: количество, места и выручка."""
        return self.aggregate(
            schedules=models.Count("id"),
            active=models.Count(
                "id",
                filter=Q(status=ScheduleStatus.ACTIVE),
            ),
            completed=models.Count(
                "id",
                filter=Q(status=ScheduleStatus.COMPLETED),
            ),
            cancelled=models.Count(
                "id",
                filter=Q(status=ScheduleStatus.CANCELLED),
            ),
            booked_total=Sum("booked"),
            revenue=Sum(
                models.F("booked") * models.F("excursion__base_price"),
                output_field=models.DecimalField(
                    max_digits=12,
                    decimal_places=2,
                ),
            ),
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
        help_text="Сколько мест уже занято на этом занятии",
    )
    status = models.CharField(
        max_length=20,
        choices=ScheduleStatus.choices,
        default=ScheduleStatus.ACTIVE,
        verbose_name="Статус",
    )
    note = models.TextField(
        blank=True,
        verbose_name="Примечание",
    )

    objects = ScheduleQuerySet.as_manager()

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
        return self.status == ScheduleStatus.CANCELLED

    @property
    def is_completed(self):
        return self.status == ScheduleStatus.COMPLETED

    def cancel(self):
        """Отменить занятие, не удаляя его из истории."""
        self.status = ScheduleStatus.CANCELLED
        self.save(update_fields=["status"])

    def mark_done(self):
        """Отметить занятие проведённым."""
        self.status = ScheduleStatus.COMPLETED
        self.save(update_fields=["status"])
