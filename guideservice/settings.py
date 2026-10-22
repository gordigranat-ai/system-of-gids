"""
Настройки Django-проекта «Сервис управления туристическими гидами».

Проект вырос из консольного приложения ПР1–ПР3, поэтому рядом с пакетом
настроек остались main.py, models.py, storage.py и каталог data/ — они
продолжают использоваться как предметная модель.
"""

import os
from pathlib import Path

# Путь к корню репозитория: BASE_DIR / "data" — файлы данных ПР3.
BASE_DIR = Path(__file__).resolve().parent.parent


# ВНИМАНИЕ: ключ только для учебного проекта, в открытый доступ его не выкладывают.
SECRET_KEY = 'django-insecure-*2qa5@+)i-9og#4_k1o#14wqzr@sb9$w4!8i2(3za_gp4)e7%7'

# Отладку можно переключать без правки файла: DJANGO_DEBUG=0 нужен, чтобы
# увидеть собственную страницу 404 — при DEBUG = True Django показывает
# техническую страницу отладки.
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# При DEBUG = False Django принимает запросы только к адресам из этого списка.
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


# Приложения проекта: главная страница и четыре сущности предметной области.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'homepage',
    'guides',
    'routes',
    'excursions',
    'schedules',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'guideservice.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Каталог шаблонов уровня проекта: base.html и общие включаемые части.
        'DIRS': [BASE_DIR / "templates"],
        # Шаблоны приложений ищутся в их собственных каталогах templates/.
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'guideservice.wsgi.application'


# Служебная база Django (сессии, администратор). Данные проекта пока
# хранятся в JSON, поэтому django ORM в ПР5 не используется.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Локализация: русский язык интерфейса и московское время.
LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True


# Статические файлы (собственный CSS, JavaScript и логотип проекта).
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
