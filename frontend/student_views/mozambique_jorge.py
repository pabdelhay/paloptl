from django.shortcuts import render
from django.views import View

from frontend.forms import BudgetPerYearForm,Year


class IndexMozambique(View):
    def get(self, request):
        print()
        ctx = {
            'form': Year,
            }
        return render(request, 'frontend/students/mozambique_index.html', context=ctx)
