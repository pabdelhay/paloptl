from django.urls import path
from django.views.generic import TemplateView

from frontend.views import IndexView, CountryView, TesteView, CartView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('teste/', TesteView.as_view(), name='teste'),
    path('chart/', CartView.as_view(), name='chart'),
    path('dataviz/', TemplateView.as_view(template_name="frontend/chart_sample.htm"), name='dataviz'),
    path('<slug>/', CountryView.as_view(), name='country-details'),
]
