"""Условие показа Django Debug Toolbar.

Панель нужна на страницах сайта, чтобы смотреть SQL-запросы, но в
административной панели она перекрывает содержимое, поэтому там её прячем.
"""

from django.conf import settings


def show_toolbar(request):
    """Показывать панель только в режиме отладки и вне админки."""
    if not settings.DEBUG:
        return False
    return not request.path.startswith("/admin/")
