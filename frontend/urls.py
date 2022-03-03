from django.urls import path
from django.views.generic import TemplateView

from frontend.views import IndexView, CountryView, CountriesExpensesView, ExpensesAndRevenues, TestView, ExampleView, \
    BudgetCountryYear

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('comparativo-despesas/', CountriesExpensesView.as_view(), name='countries-expenses'),
    path('teste/', TestView.as_view(), name='test'),
    path('dataviz/', TemplateView.as_view(template_name="frontend/chart_sample.htm"), name='dataviz'),
    path('example/', ExampleView.as_view(), name='example'),
    path('budget_country_year/', BudgetCountryYear.as_view(), name='budget_country_year'),
    path('<slug>/', CountryView.as_view(), name='country-details'),
    path('<slug>/despesas-e-receitas/', ExpensesAndRevenues.as_view(), name='despesas-e-receitas'),

]
