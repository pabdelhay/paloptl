from django.shortcuts import render
from django.views import View

from frontend.forms import YearPercentForm


class MozambiqueCustodio(View):
    def get(self, request):

        form = YearPercentForm()
        ctx = {
            'form': form,
            }
        return render(request, 'frontend/students/custodio.html', context=ctx)