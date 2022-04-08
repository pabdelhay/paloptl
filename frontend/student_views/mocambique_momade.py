from django.shortcuts import render
from django.views import View

from frontend.forms import BudgetPerCountryForm


class YearPercentGetParameter(View):
    def get(self, request):
        form = BudgetPerCountryForm()
        ctx = {
            'form': form
        }

        return render(request, 'frontend/students/moz_momade.html', context=ctx)
