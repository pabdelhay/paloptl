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

    def post(self, request):
        ctx = {}
        return render(request, 'frontend/index.html', context=ctx)


class CountryView(SingleObjectMixin, View):
    model = Country

    def get(self, request, *args, **kwargs):
        # Look up the author we're interested in.
        self.object = self.get_object()
        ctx = {
            'country': self.object
        }
        return render(request, 'frontend/country-details.html', context=ctx)
