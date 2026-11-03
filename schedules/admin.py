"""Административная панель: модель занятия и встроенные формы.

Встроенные формы используются на страницах гида и экскурсии: там видно,
какие занятия к ним относятся.
"""

from django.contrib import admin

from schedules.models import Schedule, ScheduleStatus

INLINE_FIELDS = ("date", "start_time", "status", "booked", "note")


class GuideScheduleInline(admin.TabularInline):
    """Занятия гида прямо на странице гида."""

    model = Schedule
    fk_name = "guide"
    fields = INLINE_FIELDS
    extra = 0
    ordering = ("date", "start_time")
    show_change_link = True


class ExcursionScheduleInline(admin.TabularInline):
    """Занятия экскурсии прямо на странице экскурсии."""

    model = Schedule
    fk_name = "excursion"
    fields = INLINE_FIELDS
    extra = 0
    ordering = ("date", "start_time")
    show_change_link = True


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """Список занятий: связанные объекты, фильтры, действия."""

    list_display = (
        "date",
        "start_time",
        "excursion",
        "guide",
        "booked",
        "free_seats_display",
        "status",
    )
    list_display_links = ("date",)
    list_editable = ("booked", "status")
    list_filter = ("status", "date", "guide", "excursion__route")
    search_fields = ("excursion__title", "guide__name", "note")
    date_hierarchy = "date"
    ordering = ("-date", "start_time")
    list_per_page = 20
    list_select_related = ("excursion", "guide")
    autocomplete_fields = ("excursion", "guide")
    readonly_fields = ("free_seats_display", "revenue_display")
    actions = ("mark_completed", "mark_cancelled")

    fieldsets = (
        ("Когда", {"fields": ("date", "start_time", "status")}),
        ("Кто и что", {"fields": ("excursion", "guide")}),
        ("Места", {
            "fields": ("booked", "free_seats_display", "revenue_display"),
            "description": "Свободные места и выручка считаются моделью",
        }),
        ("Дополнительно", {"fields": ("note",)}),
    )

    @admin.display(description="Свободно мест")
    def free_seats_display(self, obj):
        """Сколько мест осталось — вычисляется моделью."""
        return obj.free_seats

    @admin.display(description="Выручка, ₽")
    def revenue_display(self, obj):
        """Выручка занятия — вычисляется моделью."""
        return obj.revenue

    @admin.action(description="Отметить проведёнными")
    def mark_completed(self, request, queryset):
        """Массовое действие: перевести занятия в статус «проведена»."""
        updated = queryset.update(status=ScheduleStatus.COMPLETED)
        self.message_user(request, f"Отмечено проведёнными: {updated}")

    @admin.action(description="Отменить занятия")
    def mark_cancelled(self, request, queryset):
        """Массовое действие: перевести занятия в статус «отменена»."""
        updated = queryset.update(status=ScheduleStatus.CANCELLED)
        self.message_user(request, f"Отменено занятий: {updated}")
