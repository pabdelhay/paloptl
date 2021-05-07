import json

from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from apps.geo.models import Country


class IndexView(View):
    def get(self, request):
        ctx = {
            'countries': Country.objects.all()
        }
        return render(request, 'frontend/index.html', context=ctx)


class CountryView(SingleObjectMixin, View):
    model = Country

    def get(self, request, *args, **kwargs):
        country = self.get_object()
        base_qs = country.budgets.filter(is_active=True)\
            .exclude(function_budget__isnull=True, agency_budget__isnull=True)
        budgets = base_qs.order_by('year')
        last_budget = base_qs.order_by('year').last()
        default_budget_account = 'functions' if last_budget and last_budget.function_budget else 'agencies'

        budgets_serialized = {}
        for b in budgets:
            budgets_serialized[b.id] = {
                'id': b.id,
                'year': b.year,
                'function_budget': b.function_budget,
                'agency_budget': b.agency_budget
            }

        ctx = {
            'country': country,
            'budgets': budgets,
            'default_budget_account': default_budget_account,
            'last_budget': last_budget,
            'budgets_serialized': json.dumps(budgets_serialized),
            'treemap_colors_map': json.dumps(settings.TREEMAP_EXECUTION_COLORS_HOVER)
        }
        return render(request, 'frontend/country-details.html', context=ctx)
