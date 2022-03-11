from django.shortcuts import render
from django.views import View

from frontend.forms import BudgetPerYearForm


class TransparencyIndex(View):
    def get(self, request):
        form = BudgetPerYearForm()
        ctx = {
            'form': form
        }
        return render(request, 'frontend/students/transparency-index.html', context=ctx)
