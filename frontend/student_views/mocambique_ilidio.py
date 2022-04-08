from django.shortcuts import render
from django.views import View

from frontend.forms import YearPercentForm


class YearPercentGetParameter(View):
    def get(self, request):
        form = YearPercentForm()
        ctx = {
            'form': form,
        }
        return render(request, 'frontend/students/year_percent_get_parameter.html', context=ctx)
