from django.shortcuts import render
from django.views import View

from frontend.forms import yearpercentForm


class Mozambique_Custodio(View):
    def get(self, request):

        form = yearpercentForm()
        ctx = {
            'form': form,
            }
        return render(request, 'frontend/students/custodio.html', context=ctx)