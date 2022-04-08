

from django.shortcuts import render
from django.views import View

from frontend.forms import Countries


class FilipeMozambique(View):
    def get(self, request, *args, **kwargs):
        form = Countries()
        ctx = {
            'form': form
        }
        return render(request, 'frontend/students/mozambique_filipe.html', context=ctx)
