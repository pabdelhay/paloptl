from django.urls import path
from django.views.generic import TemplateView

from frontend.views import IndexView, CountryView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('<slug>/', CountryView.as_view(), name='country-details'),
    path('dataviz/', TemplateView.as_view(template_name="frontend/chart_sample.htm"), name='dataviz'),
]
