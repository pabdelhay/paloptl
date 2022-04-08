from requests import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.api import BudgetSerializer
from apps.budget.models import Budget, BudgetSummary, Expense
from apps.geo.models import Country


class MozambiqueCustodioViewset(ReadOnlyModelViewSet):
    model = Budget
    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()

    @action(detail=False)
    def expense(self, request, pk=None):
        slug = request.query_params.get('slug')
        qs = Expense.objects.filter(group='functional', code='',budget__year=slug)
        detail_expenses = []
        for q in qs:
                detail = {'name': q.country.name, 'year': q.year, 'budget_operation': q.budget.budget_operation, 'budget_investment': q.budget.budget_investment,  'execution_operation': q.budget.execution_operation, 'execution_investment': q.budget.execution_investment}
                detail.append(detail_expenses)
        return Response(detail_expenses)

