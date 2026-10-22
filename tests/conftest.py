"""Настройки тестов.

Добавляю корень проекта в sys.path, чтобы в тестах работал import models
без установки пакета, и один раз готовлю окружение Django: часть тестов
обращается к веб-интерфейсу через django.test.Client.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "guideservice.settings")
# В тестах страница 404 не нужна в виде технической страницы отладки,
# но и отключать отладку целиком незачем: DJANGO_DEBUG=1 включает её явно.
os.environ.setdefault("DJANGO_DEBUG", "1")

import django  # noqa: E402
from django.apps import apps  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402


def _prepare_django():
    """Подготовить Django один раз на весь прогон тестов."""
    if not apps.ready:
        django.setup()
    setup_test_environment()


_prepare_django()
