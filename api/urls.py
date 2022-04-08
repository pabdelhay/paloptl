from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from api.api import BudgetViewset
from api.api_admin import AdminViewset
from api.students.angola_bernardo import AngolaBernardoViewset
from api.students.angola_estima import AngolaEstimaViewset
from api.students.angola_lupossa import AngolaLupossaViewset
from api.students.expenses import MozambiqueCustodioViewset
from api.students.moz_custodio import ExpenseViewset

router = DefaultRouter()

router.register(r'api-admin', AdminViewset, basename='api_admin')
router.register(r'budgets', BudgetViewset, basename='budgets')

# Students
router.register(r'angola-estima', AngolaEstimaViewset, basename='angola_estima_api')
router.register(r'angola-lupossa', AngolaLupossaViewset, basename='angola_lupossa_api')
router.register(r'angola-bernardo', AngolaBernardoViewset, basename='angola_bernardo_api')

router.register(r'mozambique-custodio', ExpenseViewset, basename='mozambique_custodio_api')
router.register(r'country-expense', MozambiqueCustodioViewset, basename='country_expense_api')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls'))
]
