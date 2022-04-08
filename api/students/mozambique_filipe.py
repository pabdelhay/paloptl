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
    def currency(self, request, pk=None):
        country = request.query_params.get('country')
        qs = BudgetSummary.objects.filter(budget__country__id=country)
        line = []
        for ws in qs:
            r = ws.expense_functional_budget
            d = ws.expense_functional_execution
            if d is not None:
                year = ws.budget.year
                percent = (d/r)*100
                mycurrency = {"year": year, "country": country, "percent": percent}
                line.append(mycurrency)
        return Response(line)
