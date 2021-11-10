from django.urls import path
from django.views.generic import TemplateView

from frontend.views import IndexView, CountryView, CountriesExpensesView, WelcomeView, CountryExpenseAndRevenueView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('comparativo-despesas/', CountriesExpensesView.as_view(), name='countries-expenses'),
    path('dataviz/', TemplateView.as_view(template_name="frontend/chart_sample.htm"), name='dataviz'),
    path('welcome/', WelcomeView.as_view(), name='hello'),
    path('<slug>/despesa-e-receitas', CountryExpenseAndRevenueView.as_view(), name='country-expense-revenue'),
    path('<slug>/', CountryView.as_view(), name='country-details'),
]
