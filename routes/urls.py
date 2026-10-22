"""Маршруты приложения routes."""

from django.urls import path

from . import views

app_name = "routes"

urlpatterns = [
    path("", views.routes, name="list"),
    path("<int:route_id>/", views.route_detail, name="detail"),
]
