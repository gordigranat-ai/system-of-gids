"""Административная панель: модель гида."""

from django.contrib import admin
from django.db.models import Count

from guides.models import Guide
from schedules.admin import GuideScheduleInline


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    """Список гидов: столбцы, поиск, фильтры и встроенные занятия."""

    list_display = (
        "name",
        "specialization",
        "experience_years",
        "rating",
        "is_active",
        "schedules_total",
    )
    list_display_links = ("name",)
    list_editable = ("is_active",)
    list_filter = ("is_active", "specialization")
    search_fields = ("name", "specialization", "languages")
    ordering = ("name",)
    list_per_page = 10
    readonly_fields = ("rating",)
    inlines = [GuideScheduleInline]

    fieldsets = (
        ("Кто это", {
            "fields": ("name", "specialization", "languages"),
        }),
        ("Опыт", {
            "fields": ("experience_years", "rating", "is_active"),
            "description": "Рейтинг меняется только здесь",
        }),
    )

    def get_queryset(self, request):
        """Считаем занятия одним запросом, без запроса на каждую строку."""
        return super().get_queryset(request).annotate(
            schedules_count=Count("schedules"),
        )

    @admin.display(description="Занятий", ordering="schedules_count")
    def schedules_total(self, obj):
        """Количество занятий гида в списке."""
        return obj.schedules_count
