"""Формы расписания: фильтр занятий и создание/редактирование занятия.

`ScheduleFilterForm` — обычная `forms.Form` для GET-параметров списка.
`ScheduleForm` — `ModelForm` для создания и редактирования занятия:
подписи и виджеты настроены, дата проверяется на «не в прошлом»,
а гид — на занятость в это время.
"""

from datetime import datetime, timedelta

from django import forms
from django.utils import timezone

from excursions.models import Excursion
from guides.models import Guide
from schedules.models import Schedule, ScheduleStatus

SORT_CHOICES = [
    ("date", "по дате"),
    ("date_desc", "по дате, новые сверху"),
    ("booked", "по числу броней"),
    ("excursion", "по экскурсии"),
    ("guide", "по гиду"),
]


class ScheduleFilterForm(forms.Form):
    """Фильтр списка занятий: поиск, статус, гид, период и сортировка."""

    q = forms.CharField(
        label="Поиск",
        required=False,
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "экскурсия или гид"},
        ),
    )
    status = forms.ChoiceField(
        label="Статус",
        required=False,
        choices=[("", "любой")] + list(ScheduleStatus.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    guide = forms.ModelChoiceField(
        label="Гид",
        required=False,
        queryset=Guide.objects.none(),
        empty_label="любой",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    date_from = forms.DateField(
        label="С даты",
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    date_to = forms.DateField(
        label="По дату",
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    sort = forms.ChoiceField(
        label="Сортировка",
        required=False,
        choices=SORT_CHOICES,
        initial="date",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Список гидов подставляется при создании формы, а не один раз
        # при импорте модуля — иначе данные устаревают.
        self.fields["guide"].queryset = Guide.objects.order_by("name")

    def clean(self):
        """Проверить, что период задан в правильном порядке."""
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError(
                "Дата начала не может быть позже даты окончания.",
            )
        return cleaned_data

    def filter_queryset(self, queryset):
        """Применить проверенные значения формы к набору занятий."""
        if not self.is_valid():
            return queryset

        data = self.cleaned_data

        if data["q"]:
            from django.db.models import Q

            queryset = queryset.filter(
                Q(excursion__title__icontains=data["q"])
                | Q(guide__name__icontains=data["q"]),
            )
        if data["status"]:
            queryset = queryset.filter(status=data["status"])
        if data["guide"]:
            queryset = queryset.filter(guide=data["guide"])
        if data["date_from"]:
            queryset = queryset.filter(date__gte=data["date_from"])
        if data["date_to"]:
            queryset = queryset.filter(date__lte=data["date_to"])

        sort = data["sort"] or "date"
        order = {
            "date": ("date", "start_time"),
            "date_desc": ("-date", "-start_time"),
            "booked": ("-booked", "date"),
            "excursion": ("excursion__title", "date"),
            "guide": ("guide__name", "date"),
        }.get(sort, ("date", "start_time"))
        return queryset.order_by(*order)


class ScheduleForm(forms.ModelForm):
    """Создание и редактирование занятия."""

    class Meta:
        model = Schedule
        fields = ["excursion", "guide", "date", "start_time", "booked", "note"]
        labels = {
            "excursion": "Экскурсия",
            "guide": "Гид",
            "date": "Дата",
            "start_time": "Время начала",
            "booked": "Забронировано мест",
            "note": "Примечание",
        }
        help_texts = {
            "date": "Дата не может быть в прошлом.",
            "start_time": "Время, когда начинается занятие.",
            "booked": "Сколько мест уже занято на этом занятии.",
        }
        widgets = {
            "excursion": forms.Select(attrs={"class": "form-select"}),
            "guide": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "start_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"},
            ),
            "booked": forms.NumberInput(
                attrs={"class": "form-control", "min": 0},
            ),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["excursion"].queryset = Excursion.objects.order_by("title")
        self.fields["guide"].queryset = Guide.objects.filter(
            is_active=True,
        ).order_by("name")

    def clean_date(self):
        """Дата занятия не может быть в прошлом."""
        value = self.cleaned_data["date"]
        if value < timezone.localdate():
            raise forms.ValidationError(
                "Нельзя планировать занятие на прошедшую дату.",
            )
        return value

    def clean(self):
        """Проверить число мест и занятость гида в это время."""
        cleaned_data = super().clean()
        excursion = cleaned_data.get("excursion")
        guide = cleaned_data.get("guide")
        day = cleaned_data.get("date")
        start_time = cleaned_data.get("start_time")
        booked = cleaned_data.get("booked") or 0

        if excursion and booked > excursion.max_participants:
            self.add_error(
                "booked",
                f"У экскурсии всего {excursion.max_participants} мест.",
            )

        if not (guide and day and start_time and excursion):
            return cleaned_data

        duration = timedelta(hours=float(excursion.route.duration_hours))
        start = datetime.combine(day, start_time)
        end = start + duration

        others = (
            Schedule.objects
            .filter(guide=guide, date=day)
            .exclude(status=ScheduleStatus.CANCELLED)
            .select_related("excursion", "excursion__route")
        )
        if self.instance.pk:
            # При редактировании не сравниваем занятие само с собой.
            others = others.exclude(pk=self.instance.pk)

        for other in others:
            other_start = datetime.combine(other.date, other.start_time)
            other_end = other_start + timedelta(
                hours=float(other.excursion.route.duration_hours),
            )
            if start < other_end and other_start < end:
                raise forms.ValidationError(
                    f"Гид занят: {other.date} в {other.start_time:%H:%M} — "
                    f"«{other.excursion.title}».",
                )

        return cleaned_data
