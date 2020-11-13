from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, CreateView
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
        budgets = country.budgets.all().order_by('year')
        last_budget = country.budgets.order_by('year').last()
        ctx = {
            'country': country,
            'budgets': budgets,
            'last_budget': last_budget,
        }
        return render(request, 'frontend/country-details.html', context=ctx)
