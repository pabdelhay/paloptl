from django.shortcuts import render
from django.views import View

from frontend.forms import BudgetPerYearForm


class ChartBudgetYearView(View):
    def get(self, request):
        form = BudgetPerYearForm()
        ctx = {
            'form': form
        }
        return render(request, 'frontend/students/chart-budget-per-year-and-currency.html', context=ctx)
