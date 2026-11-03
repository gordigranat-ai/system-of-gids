"""Маршруты приложения routes."""

from django.urls import path

from . import views

app_name = "routes"

urlpatterns = [
    path("", views.routes, name="list"),
    path("<slug:route_slug>/", views.route_detail, name="detail"),
]
