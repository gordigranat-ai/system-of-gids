"""Маршруты приложения excursions."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.excursions, name="excursions"),
    path("<int:excursion_id>/", views.excursion_detail, name="excursion_detail"),
]
