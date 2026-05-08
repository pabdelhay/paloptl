import json

from django.conf import settings
from django.shortcuts import render
from django.utils.translation import get_language
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from apps.budget.models import Attachment, TransparencyIndex
from apps.geo.models import Country
from frontend.forms import BudgetPerYearForm
from frontend.tutorial import COUNTRY_DETAILS_TUTORIAL, INDEX_DIMENSIONS


class IndexView(View):
    @staticmethod
    def get_visible_attachments():
        language = (get_language() or settings.LANGUAGE_CODE).split('-')[0]
        supported_languages = [code for code, _label in settings.LANGUAGES]
        if language not in supported_languages:
            language = settings.MODELTRANSLATION_DEFAULT_LANGUAGE

        file_field = f'file_{language}'
        return (
            Attachment.objects.filter(is_visible=True)
            .exclude(**{file_field: ''})
            .exclude(**{f'{file_field}__isnull': True})
            .order_by('id')
        )

    def get(self, request):
        index_years = list(
            TransparencyIndex.objects.values_list('year', flat=True)
            .distinct()
            .order_by('-year')
        )
        default_index_year = index_years[0] if index_years else None

        country_report_downloads = []
        if default_index_year is not None:
            indexes_by_country_id = {
                ti.country_id: ti
                for ti in TransparencyIndex.objects.filter(year=default_index_year)
            }
            for c in Country.objects.all():
                ti = indexes_by_country_id.get(c.pk)
                country_report_downloads.append(
                    {
                        'country': c,
                        'report_url': ti.report.url if ti and ti.report else '',
                    }
                )

        ctx = {
            'attachments': self.get_visible_attachments(),
            'countries': Country.objects.all(),
            'country_report_downloads': country_report_downloads,
            'index_dimensions': INDEX_DIMENSIONS,
            'index_years': index_years,
            'default_index_year': default_index_year,
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


class ExpensesAndRevenues(View, ):
    def get(self, request, *args, **kwargs):
        cn = {
            "country": Country.objects.get(slug=self.kwargs.get("slug"))
        }
        return render(request, 'frontend/expenses-and-revenues.html', context=cn)
