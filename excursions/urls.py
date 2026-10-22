"""Маршруты приложения excursions."""

from django.urls import path

from . import views

app_name = "excursions"

urlpatterns = [
    path("", views.excursions, name="list"),
    path("<int:excursion_id>/", views.excursion_detail, name="detail"),
]
