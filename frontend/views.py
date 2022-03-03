import json

from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from apps.geo.models import Country
from frontend.forms import CountryForm
from frontend.tutorial import COUNTRY_DETAILS_TUTORIAL, INDEX_DIMENSIONS
import requests


class IndexView(View):
    def get(self, request):
        ctx = {
            'countries': Country.objects.all(),
            'index_dimensions': INDEX_DIMENSIONS
        }
        return render(request, 'frontend/index.html', context=ctx)


class CountryView(SingleObjectMixin, View):
    model = Country

    def get(self, request, *args, **kwargs):
        country = self.get_object()
        base_qs = country.budgets.filter(is_active=True)
        budgets = base_qs.order_by('year')
        last_budget = base_qs.order_by('year').select_related('summary').last()
        summary = last_budget.summary

        default_budget_account = 'expenses'
        default_group = 'functional' if summary and summary.expense_functional_budget else 'organic'

        budgets_serialized = {}
        for b in budgets:
            budgets_serialized[b.id] = {
                'id': b.id,
                'year': b.year,
                'available_groups': b.get_available_groups(),
                'available_budget_accounts': b.get_available_budget_accounts(),
                'expense_functional_budget': b.summary.expense_functional_budget,
                'expense_organic_budget': b.summary.expense_organic_budget,
                'revenue_nature_budget': b.summary.revenue_nature_budget,
                'revenue_source_budget': b.summary.revenue_source_budget,
            }

        ctx = {
            'default_budget_account': default_budget_account,
            'default_group': default_group,
            'country': country,
            'budgets': budgets,
            'last_budget': last_budget,
            'budgets_serialized': json.dumps(budgets_serialized),
            'treemap_colors_map': json.dumps(settings.TREEMAP_EXECUTION_COLORS_HOVER),
            'tutorial': COUNTRY_DETAILS_TUTORIAL
        }
        return render(request, 'frontend/country-details.html', context=ctx)


class CountriesExpensesView(View):
    def get(self, request):
        return render(request, 'frontend/countriesExpenses.html', context=None)


class TestView(View):
    def get(self, request):
        ctx = {
            'countries': Country.objects.all()
        }
        return render(request, 'frontend/teste.html', context=ctx)


class ExpensesAndRevenues(View):
    def get(self, request, *args, **kwargs):
        cn = {
            "country": Country.objects.get(slug=self.kwargs.get("slug"))
        }
        return render(request, 'frontend/expenses-and-revenues.html', context=cn)


class ExampleView(View):

    def get(self, request):
        base_currency = request.GET.get("cur", "USD")
        url = f"http://127.0.0.1:8000/api/budgets/palop_base_currency/?cur={base_currency}"

        get_res_url = requests.get(url)

        ctx = {
            'countries': Country.objects.all(),
            'results': get_res_url.json()
        }
        return render(request, 'frontend/example.html', context=ctx)


class BudgetCountryYear(View):
    def get(self, request):

        form = CountryForm()
        ctx = {
            'form': form,
            }
        return render(request, 'frontend/budget_country_year.html', context=ctx)
