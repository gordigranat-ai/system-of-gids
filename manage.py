#!/usr/bin/env python
"""Управление Django-проектом «Экскурсионное бюро»."""
import os
import sys

MISSING_DJANGO = """\
Django не найден в этом интерпретаторе Python.

Проект работает в виртуальном окружении .venv. Запускайте команды так:

    .venv\\Scripts\\python.exe manage.py runserver

или двойным щелчком по run_web.bat.

Если окружения ещё нет:

    py -3.12 -m venv .venv
    .venv\\Scripts\\python.exe -m pip install -r requirements.txt
    .venv\\Scripts\\python.exe manage.py migrate
    .venv\\Scripts\\python.exe -m db.import_json
"""


def main():
    """Выполнить команду управления Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guideservice.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        print(MISSING_DJANGO)
        sys.exit(1)

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
