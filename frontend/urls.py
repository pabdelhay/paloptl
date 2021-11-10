from django.urls import path
from django.views.generic import TemplateView

from frontend.views import IndexView, CountryView, CountriesExpensesView, ExpensesRevenuesView

urlpatterns = [
    path('<slug>/despesas-receitas/', ExpensesRevenuesView.as_view(), name='ExpensesRevenues'),
    path('', IndexView.as_view(), name='index'),
    path('comparativo-despesas/', CountriesExpensesView.as_view(), name='countries-expenses'),
    path('dataviz/', TemplateView.as_view(template_name="frontend/chart_sample.htm"), name='dataviz'),
    path('<slug>/', CountryView.as_view(), name='country-details')
]
