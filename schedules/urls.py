"""Маршруты приложения schedules."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.schedules, name="schedules"),
    path("<int:schedule_id>/", views.schedule_detail, name="schedule_detail"),
]
