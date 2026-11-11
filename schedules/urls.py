"""Маршруты приложения schedules."""

from django.urls import path

from . import views

app_name = "schedules"

urlpatterns = [
    path("", views.schedules, name="list"),
    path("active/", views.active_schedules, name="active"),
    path("statistics/", views.statistics, name="statistics"),
    path("new/", views.schedule_create, name="create"),
    path("<int:schedule_id>/", views.schedule_detail, name="detail"),
    path("<int:schedule_id>/edit/", views.schedule_edit, name="edit"),
    path("<int:schedule_id>/cancel/", views.schedule_cancel, name="cancel"),
]
