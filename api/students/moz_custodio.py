from django.template.defaultfilters import slugify
from pytz import country_names
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.api import BudgetSerializer
from apps.budget.models import Budget, BudgetSummary
from frontend.forms import year_choices


class ExpenseViewset(ReadOnlyModelViewSet):
    model = Budget
    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()

    @action(detail=False)
    def expense(self, request, pk=None):
        id = request.query_params.get('country')
        qs = BudgetSummary.objects.filter(budget__country__id=id)
        year_percent = []
        for q in qs:
            budget = q.expense_functional_budget
            execution = q.expense_functional_execution
            if execution is not None:
                percent = (execution / budget) * 100
                d1 = {'year': q.budget.year, 'percent': round(percent, 2)}
                year_percent.append(d1)
        return Response(year_percent)











