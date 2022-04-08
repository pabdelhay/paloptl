from django.shortcuts import render
from django.views import View

from frontend.forms import BudgetPerYearForm, TestForm


class PabloView(View):
    def get(self, request):
        ctx = {
            'form': TestForm()
        }
        return render(request, 'frontend/students/moz_pablo.html', context=ctx)
