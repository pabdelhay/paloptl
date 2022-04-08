from django import forms

from apps.budget.models import Budget
from apps.geo.models import Country
from config.settings import CURRENCY_CHOICES


def year_choices():
    return list(Budget.objects.order_by('year').distinct('year').values_list('year', 'year'))


class BudgetPerYearForm(forms.Form):
    base_currency = forms.ChoiceField(choices=CURRENCY_CHOICES)
    year = forms.ChoiceField(choices=year_choices())


class yearpercentForm(forms.Form):
    country = forms.ModelChoiceField(queryset=Country.objects.all())
    year = forms.ChoiceField(choices=year_choices())
