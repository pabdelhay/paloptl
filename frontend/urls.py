from django.urls import path
from django.views.generic import TemplateView

from frontend.views import IndexView, CountryView, ExpesensesByCountryView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('dataviz/', TemplateView.as_view(template_name="frontend/chart_sample.htm"), name='dataviz'),
    path("expenses_by_country/", ExpesensesByCountryView.as_view(), name="expenses_by_country"),
    path('<slug>/', CountryView.as_view(), name='country-details'),
]
