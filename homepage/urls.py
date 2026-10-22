"""Маршруты приложения homepage.

app_name задаёт пространство имён: в шаблонах ссылки записываются как
{% url 'homepage:index' %}, даже если другое приложение назовёт свой
маршрут так же.
"""

from django.urls import path

from . import views

app_name = "homepage"

urlpatterns = [
    path("", views.index, name="index"),
]
