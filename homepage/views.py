"""Главная страница и общий каркас HTML-страниц проекта.

В ПР5 страницы собираются строкой в Python-коде. Функция page() играет роль
общего шаблона: она подключает Bootstrap, выводит навигацию и оборачивает
содержимое страницы в контейнер. Остальные приложения импортируют её.
"""

from django.http import HttpResponse

BOOTSTRAP_CSS = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
    "/dist/css/bootstrap.min.css"
)


def page(title, content):
    """Собрать HTML-документ из заголовка вкладки и содержимого страницы."""
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="{BOOTSTRAP_CSS}">
</head>
<body>
    <nav class="nav">
        <a class="nav-link" href="/">Главная</a>
        <a class="nav-link" href="/guides/">Гиды</a>
        <a class="nav-link" href="/routes/">Маршруты</a>
        <a class="nav-link" href="/excursions/">Экскурсии</a>
        <a class="nav-link" href="/schedules/">Расписание</a>
    </nav>
    <main class="container">{content}</main>
</body>
</html>"""


def index(request):
    """Главная страница: о проекте и ссылки на разделы."""
    content = """
    <h1 class="display-4">Сервис управления гидами</h1>
    <p class="lead">
        Экскурсионное бюро: гиды, маршруты, экскурсии и расписание.
    </p>
    <p>
        Программа выросла из консольного приложения ПР1–ПР3. В веб-интерфейсе
        пока доступен просмотр данных: списки объектов и карточки отдельных
        записей. Добавление и редактирование появятся после изучения форм.
    </p>
    <a href="/guides/" class="btn btn-primary me-2">Гиды</a>
    <a href="/routes/" class="btn btn-primary me-2">Маршруты</a>
    <a href="/excursions/" class="btn btn-primary me-2">Экскурсии</a>
    <a href="/schedules/" class="btn btn-secondary">Расписание</a>
    """
    return HttpResponse(page("Гиды и экскурсии", content))


def page_not_found(request, exception):
    """Собственная страница 404 для адресов, которым не нашлось маршрута."""
    content = """
    <h1 class="text-danger">404 – страница не найдена</h1>
    <p>Проверьте адрес или вернитесь на главную страницу.</p>
    <a href="/" class="btn btn-primary">На главную</a>
    """
    return HttpResponse(page("404 – страница не найдена", content), status=404)
