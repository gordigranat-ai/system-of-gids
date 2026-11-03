"""Миграция: статусы занятия переводятся на TextChoices.

Раньше в базе лежали русские названия статусов, теперь хранятся короткие
коды (active, completed, cancelled), а подписи для интерфейса заданы
в TextChoices. Существующие записи преобразуются этой же миграцией.
"""

from django.db import migrations, models

OLD_TO_NEW = {
    "запланирована": "active",
    "проведена": "completed",
    "отменена": "cancelled",
}

NEW_TO_OLD = {new: old for old, new in OLD_TO_NEW.items()}


def forwards(apps, schema_editor):
    """Русские значения статусов → коды TextChoices."""
    Schedule = apps.get_model("schedules", "Schedule")
    for old, new in OLD_TO_NEW.items():
        Schedule.objects.filter(status=old).update(status=new)


def backwards(apps, schema_editor):
    """Коды TextChoices → прежние русские значения."""
    Schedule = apps.get_model("schedules", "Schedule")
    for new, old in NEW_TO_OLD.items():
        Schedule.objects.filter(status=new).update(status=old)


class Migration(migrations.Migration):

    dependencies = [
        ("schedules", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="schedule",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "запланирована"),
                    ("completed", "проведена"),
                    ("cancelled", "отменена"),
                ],
                default="active",
                max_length=20,
                verbose_name="Статус",
            ),
        ),
        migrations.RunPython(forwards, backwards),
    ]
