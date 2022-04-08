from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from api.api import BudgetSerializer
from apps.budget.models import Budget, BudgetSummary


class MozambiqueFilipeViewset(ReadOnlyModelViewSet):
    model = Budget
    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()

    @action(detail=False)
    def budgetsummarydata(self, request, pk=None):
        country = request.query_params.get('country')
        queryset = BudgetSummary.objects.filter(budget__country__id=country)
        line = []
        for BudgetSummaryPercentage in queryset:
            revenue = BudgetSummaryPercentage.expense_functional_budget
            expense = BudgetSummaryPercentage.expense_functional_execution
            if expense is not None:
                year = BudgetSummaryPercentage.budget.year
                percent = (expense/revenue)*100
                budgetsummaryresult = {"year": year, "country": country, "percent": percent}
                line.append(budgetsummaryresult)
        return Response(line)
