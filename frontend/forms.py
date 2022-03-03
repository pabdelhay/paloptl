from django import forms
from django.conf import settings

from apps.budget.models import BudgetSummary


def year_choices():
    big_data = BudgetSummary.objects.all()

    dic_year = {}

    for db in big_data:
        dic_year[db.budget.year] = db.budget.year
    list = []

    for year in dic_year:
        list_1 = [dic_year[year], dic_year[year]]
        list.append(list_1)
    return list


class CountryForm(forms.Form):
    base_currency = forms.ChoiceField(choices=settings.CURRENCY_CHOICES)
    year = forms.ChoiceField(choices=year_choices)
