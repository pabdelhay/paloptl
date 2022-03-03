from django import forms

from apps.budget.models import Budget
from config.settings import CURRENCY_CHOICES


def year_choices():
    return list(list(Budget.objects.filter().order_by('year').distinct('year').values_list('year', 'year')))


class BudgetPerYearForm(forms.Form):
    base_currency = forms.ChoiceField(choices=CURRENCY_CHOICES)
    year = forms.ChoiceField(choices=year_choices())
