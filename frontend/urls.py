from django.urls import path

from frontend.views import IndexView, CountryView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('<slug>/', CountryView.as_view(), name='country-details'),
]