from django.shortcuts import render
from django.views import View

from frontend.forms import BudgetPerYearForm, TestForm


class SergioMussicaIndex(View):
    def get(self, request):

        ctx = {
            'form': TestForm(),
        }
        return render(request, 'frontend/students/mozambique_sergio_index.html', context=ctx)
