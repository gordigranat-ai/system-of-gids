"""Настройки тестов.

Добавляю корень проекта в sys.path, чтобы в тестах работал
import models без установки пакета.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
