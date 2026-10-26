"""Страницы главного приложения: главная страница и обработчик 404.

HTML здесь больше не собирается: view-функция выбирает шаблон и передаёт
в него данные через контекст.
"""

from django.shortcuts import render


def index(request):
    """Главная страница проекта."""
    return render(request, "homepage/index.html")


def page_not_found(request, exception):
    """Собственная страница 404 для адресов, которым не нашлось маршрута."""
    return render(request, "homepage/page_not_found.html", status=404)
