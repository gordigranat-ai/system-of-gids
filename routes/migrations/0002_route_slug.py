"""Миграция: у маршрута появляется slug для человекочитаемого адреса.

Поле добавляется в два приёма: сначала без уникальности, затем данные
заполняются, и только после этого включается unique=True — иначе
несколько пустых значений нарушили бы ограничение.
"""

from django.db import migrations, models

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e",
    "ё": "e", "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k",
    "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
    "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "",
    "э": "e", "ю": "yu", "я": "ya",
}


def transliterate(text):
    """Локальная копия транслитерации: миграция не зависит от кода моделей."""
    return "".join(TRANSLIT.get(char, char) for char in text.lower())


def fill_slugs(apps, schema_editor):
    """Заполнить slug у существующих маршрутов."""
    from django.utils.text import slugify

    Route = apps.get_model("routes", "Route")
    used = set()

    for route in Route.objects.order_by("pk"):
        base = slugify(transliterate(route.name)) or f"route-{route.pk}"
        slug = base
        number = 2
        while slug in used:
            slug = f"{base}-{number}"
            number += 1
        used.add(slug)
        route.slug = slug
        route.save(update_fields=["slug"])


def clear_slugs(apps, schema_editor):
    """Откат: очистить slug."""
    Route = apps.get_model("routes", "Route")
    Route.objects.update(slug="")


class Migration(migrations.Migration):

    dependencies = [
        ("routes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="route",
            name="slug",
            field=models.SlugField(
                blank=True,
                default="",
                max_length=200,
                verbose_name="Адрес страницы",
            ),
            preserve_default=False,
        ),
        migrations.RunPython(fill_slugs, clear_slugs),
        migrations.AlterField(
            model_name="route",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="Заполняется автоматически из названия",
                max_length=200,
                unique=True,
                verbose_name="Адрес страницы",
            ),
        ),
    ]
