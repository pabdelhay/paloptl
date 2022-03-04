from django import forms
from django.conf import settings

from apps.budget.models import Budget


def year_choice():
    years = Budget.objects.order_by('year').values_list('year', 'year').distinct()
    return years


class ExerciseAngolaForm(forms.Form):
    base_currency = forms.ChoiceField(choices=settings.CURRENCY_CHOICES)
    year = forms.ChoiceField(choices=year_choice)
