"""Маршруты приложения guides."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.guides, name="guides"),
    path("<int:guide_id>/", views.guide_detail, name="guide_detail"),
]
