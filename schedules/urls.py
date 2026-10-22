"""Маршруты приложения schedules."""

from django.urls import path

from . import views

app_name = "schedules"

urlpatterns = [
    path("", views.schedules, name="list"),
    path("active/", views.active_schedules, name="active"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:schedule_id>/", views.schedule_detail, name="detail"),
]
