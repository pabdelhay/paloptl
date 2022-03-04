from django.shortcuts import render
from django.views import View

from frontend.forms import ExerciseAngolaForm


class BudgetCountryYear(View):
    def get(self, request):

        form = ExerciseAngolaForm()
        ctx = {
            'form': form,
            }
        return render(request, 'frontend/budget_country_year.html', context=ctx)
