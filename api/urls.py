from django.conf.urls import url
from django.urls import include
from api.students.angola_lue import AngolaLueViewset
from rest_framework.routers import DefaultRouter

from api.api import BudgetViewset
from api.api_admin import AdminViewset
from api.students.angola_bernardo import AngolaBernardoViewset
from api.students.angola_estima import AngolaEstimaViewset
from api.students.angola_lupossa import AngolaLupossaViewset

router = DefaultRouter()

router.register(r'api-admin', AdminViewset, basename='api_admin')
router.register(r'budgets', BudgetViewset, basename='budgets')

# Students
router.register(r'angola-estima', AngolaEstimaViewset, basename='angola_estima_api')
router.register(r'angola-lupossa', AngolaLupossaViewset, basename='angola_lupossa_api')
router.register(r'angola-bernardo', AngolaBernardoViewset, basename='angola_bernardo_api')
router.register(r'angola-lue', AngolaLueViewset, basename='angola_lue_api')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls'))
]
