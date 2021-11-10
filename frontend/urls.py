from django.urls import path
from django.views.generic import TemplateView

from frontend.views import IndexView, CountryView, CountriesExpensesView, DespesasEReceitas

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('comparativo-despesas/', CountriesExpensesView.as_view(), name='countries-expenses'),
    path('dataviz/', TemplateView.as_view(template_name="frontend/chart_sample.htm"), name='dataviz'),
    path('<slug>/', CountryView.as_view(), name='country-details'),
    path('<slug>/despesas-e-receitas/', DespesasEReceitas.as_view(), name='despesas-e-receitas'),
]
