"""Административная панель: модель маршрута."""

from django.contrib import admin
from django.db.models import Count

from excursions.admin import ExcursionInline
from routes.models import Route


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    """Список маршрутов: столбцы, фильтры, поиск и экскурсии внутри."""

    list_display = (
        "name",
        "slug",
        "difficulty",
        "duration_hours",
        "distance_km",
        "is_active",
        "excursions_total",
    )
    list_display_links = ("name",)
    list_editable = ("is_active",)
    list_filter = ("difficulty", "is_active")
    search_fields = ("name", "description", "slug")
    ordering = ("name",)
    list_per_page = 10
    readonly_fields = ("slug",)
    inlines = [ExcursionInline]

    fieldsets = (
        ("Маршрут", {
            "fields": ("name", "slug", "description"),
        }),
        ("Характеристики", {
            "fields": (
                "duration_hours",
                "distance_km",
                "difficulty",
                "required_languages",
                "is_active",
            ),
        }),
    )

    def get_queryset(self, request):
        """Количество экскурсий считаем сразу в запросе."""
        return super().get_queryset(request).annotate(
            excursions_count=Count("excursions"),
        )

    @admin.display(description="Экскурсий", ordering="excursions_count")
    def excursions_total(self, obj):
        """Сколько экскурсий идёт по маршруту."""
        return obj.excursions_count
