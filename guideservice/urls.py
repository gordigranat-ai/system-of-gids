"""Корневая конфигурация маршрутов проекта.

Каждое приложение отвечает за свои адреса: корневой файл только «режет»
URL на префикс и остаток, который ищется в urls.py приложения.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("homepage.urls")),
    path("guides/", include("guides.urls")),
    path("routes/", include("routes.urls")),
    path("excursions/", include("excursions.urls")),
    path("schedules/", include("schedules.urls")),
]

# Собственная страница 404. Обработчик читается только из этого файла,
# поэтому действует сразу для всех приложений проекта.
handler404 = "homepage.views.page_not_found"
