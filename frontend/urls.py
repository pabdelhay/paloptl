from django.urls import path
from django.views.generic import TemplateView

from frontend.student_views import AngolaIndex
from frontend.student_views.angola_bernardo import TotalExpensePerYear
from frontend.student_views.angola_estima import ChartBudgetYearView
from frontend.student_views.angola_lupossa import BudgetCountryYear
from frontend.student_views.mocambique_momade import YearPercentGetParameter
from frontend.views import IndexView, CountryView, CountriesExpensesView, ExpensesAndRevenues, TestView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('comparativo-despesas/', CountriesExpensesView.as_view(), name='countries-expenses'),
    path('teste/', TestView.as_view(), name='test'),
    path('dataviz/', TemplateView.as_view(template_name="frontend/chart_sample.htm"), name='dataviz'),
    # Students
    path('students/angola/', AngolaIndex.as_view(), name='chart-budget'),
    path('students/angola/chart-budget-per-year-and-currency/', ChartBudgetYearView.as_view(), name='chart-budget'),
    path('students/angola/budget_country_year/', BudgetCountryYear.as_view(), name='budget_country_year'),
    path('students/angola/total-expense-per-year/', TotalExpensePerYear.as_view(), name='total-expense-per-year'),
    path('students/mocambique/year_percent_get_parameter', YearPercentGetParameter.as_view(), name='year_percent_get_parameter'),

    path('<slug>/', CountryView.as_view(), name='country-details'),
    path('<slug>/despesas-e-receitas/', ExpensesAndRevenues.as_view(), name='despesas-e-receitas'),
]
