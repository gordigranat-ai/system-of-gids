"""Маршруты приложения guides."""

from django.urls import path

from . import views

app_name = "guides"

urlpatterns = [
    path("", views.guides, name="list"),
    path("<int:guide_id>/", views.guide_detail, name="detail"),
]
