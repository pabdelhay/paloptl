from django.shortcuts import render
from django.views import View

from frontend.forms import BudgetPerYearForm


class BudgetCountryYear(View):
    def get(self, request):

        form = BudgetPerYearForm()
        ctx = {
            'form': form,
            }
        return render(request, 'frontend/students/budget_country_year.html', context=ctx)
