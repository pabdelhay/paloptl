from django.shortcuts import render
from django.urls import reverse
from django.views import View


class AngolaIndex(View):
    def get(self, request):
        views_per_student = {
            'Bernardo': reverse('total-expense-per-year'),
            'Estima': reverse('chart-budget'),
            'Lupossa': reverse('budget_country_year'),
            'Lue': reverse('transparency-index'),
        }
        ctx = {
            'views': views_per_student
        }
        return render(request, 'frontend/students/angola_index.html', context=ctx)
