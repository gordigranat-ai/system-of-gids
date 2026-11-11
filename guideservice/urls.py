"""Корневая конфигурация маршрутов проекта.

Каждое приложение отвечает за свои адреса: корневой файл только «режет»
URL на префикс и остаток, который ищется в urls.py приложения.
"""

from django.conf import settings
from django.conf.urls.static import static
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

# Панель отладки подключается только при включённой отладке.
if settings.DEBUG:
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + urlpatterns

# Загруженные файлы (фотографии гидов) в режиме разработки отдаёт Django.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

# Собственная страница 404. Обработчик читается только из этого файла,
# поэтому действует сразу для всех приложений проекта.
handler404 = "homepage.views.page_not_found"
