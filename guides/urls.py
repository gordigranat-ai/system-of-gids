"""Маршруты приложения guides."""

from django.urls import path

from . import views

app_name = "guides"

urlpatterns = [
    path("", views.guides, name="list"),
    path("available/", views.available_guides, name="available"),
    path("<int:guide_id>/", views.guide_detail, name="detail"),
    path("<int:guide_id>/edit/", views.guide_edit, name="edit"),
]
