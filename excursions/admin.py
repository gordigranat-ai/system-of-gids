"""Административная панель: модель экскурсии."""

from django.contrib import admin
from django.db.models import Count

from excursions.models import Excursion
from schedules.admin import ExcursionScheduleInline


class ExcursionInline(admin.TabularInline):
    """Экскурсии прямо на странице маршрута."""

    model = Excursion
    fields = ("title", "kind", "base_price", "max_participants", "is_active")
    extra = 0
    ordering = ("title",)
    show_change_link = True


@admin.register(Excursion)
class ExcursionAdmin(admin.ModelAdmin):
    """Список экскурсий: связанный маршрут, фильтры и встроенные занятия."""

    list_display = (
        "title",
        "route",
        "kind",
        "base_price",
        "max_participants",
        "is_active",
        "schedules_total",
    )
    list_display_links = ("title",)
    list_editable = ("is_active",)
    list_filter = ("kind", "route", "is_active")
    search_fields = ("title", "route__name")
    ordering = ("title",)
    list_per_page = 10
    list_select_related = ("route",)
    autocomplete_fields = ("route",)
    inlines = [ExcursionScheduleInline]

    fieldsets = (
        ("Экскурсия", {
            "fields": ("title", "route", "kind", "is_active"),
        }),
        ("Деньги и места", {
            "fields": (
                "base_price",
                "max_participants",
                "min_age",
                "languages",
            ),
        }),
    )

    def get_queryset(self, request):
        """Количество занятий считаем в том же запросе."""
        return super().get_queryset(request).annotate(
            schedules_count=Count("schedules"),
        )

    @admin.display(description="Занятий", ordering="schedules_count")
    def schedules_total(self, obj):
        """Сколько занятий запланировано по экскурсии."""
        return obj.schedules_count
