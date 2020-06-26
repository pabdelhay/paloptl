from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from api.api_admin import AdminViewset

router = DefaultRouter()

router.register(r'api-admin', AdminViewset, basename='api_admin')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls'))
]
