from django.urls import path
from django.views.generic import TemplateView

from frontend.views import ChartBudgetYearView, IndexView, CountryView, CountriesExpensesView, ExpensesAndRevenues, TestView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('comparativo-despesas/', CountriesExpensesView.as_view(), name='countries-expenses'),
    path('teste/', TestView.as_view(), name='test'),
    path('chart-budget-per-year-and-currency/', ChartBudgetYearView.as_view(), name='chart-budget'),
    path('dataviz/', TemplateView.as_view(template_name="frontend/chart_sample.htm"), name='dataviz'),
    path('<slug>/', CountryView.as_view(), name='country-details'),
    path('<slug>/despesas-e-receitas/', ExpensesAndRevenues.as_view(), name='despesas-e-receitas'),
]
