"""Форма редактирования гида: данные и фотография."""

from django import forms

from guides.models import Guide

MAX_PHOTO_SIZE = 2 * 1024 * 1024


class GuideForm(forms.ModelForm):
    """Редактирование гида с загрузкой фотографии."""

    class Meta:
        model = Guide
        fields = [
            "name",
            "specialization",
            "languages",
            "experience_years",
            "rating",
            "is_active",
            "photo",
        ]
        labels = {
            "name": "Имя гида",
            "specialization": "Специализация",
            "languages": "Языки",
            "experience_years": "Стаж, лет",
            "rating": "Рейтинг",
            "is_active": "Работает с экскурсиями",
            "photo": "Фотография",
        }
        help_texts = {
            "languages": "Перечислите языки через запятую.",
            "photo": "JPG или PNG, не больше 2 МБ.",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "specialization": forms.TextInput(attrs={"class": "form-control"}),
            "languages": forms.TextInput(attrs={"class": "form-control"}),
            "experience_years": forms.NumberInput(
                attrs={"class": "form-control", "min": 0},
            ),
            "rating": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 9.9, "step": 0.1},
            ),
            "photo": forms.FileInput(attrs={"class": "form-control"}),
        }

    def clean_photo(self):
        """Проверить размер загружаемого файла."""
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > MAX_PHOTO_SIZE:
            raise forms.ValidationError(
                "Файл больше 2 МБ. Загрузите изображение поменьше.",
            )
        return photo
