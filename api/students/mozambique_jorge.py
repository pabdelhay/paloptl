from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView
from api.api import BudgetSerializer

from apps.budget.models import Budget, BudgetSummary, Expense


class MozambiqueJorgeView(ReadOnlyModelViewSet):
    model = Budget
    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()

    @action(detail=False,)
    def myapi(self, request):
        listbudget = []
        country_params = request.query_params.get('country')
        budget_summary = BudgetSummary.objects.filter(budget__country__id=country_params)

        for budget in budget_summary:
            if budget.expense_functional_execution:
                percent = (budget.expense_functional_execution * 100) / budget.expense_functional_budget
                year = budget.budget.year
                country = budget.budget.country.name
                listbudget.append({"year": year, "percent": percent,"country":country})
            else:
                year = budget.budget.year
                country = budget.budget.country.name
                listbudget.append({"year": year,  "country": country})

        return Response(listbudget)
    # @action(detail=False)
    # def myapi(self, request):
    #     list_expensive = []
    #     country_params = request.query_params.get('name')
    #     code_params = request.query_params.get("code")
    #     group_params = request.query_params.get("group")
    #     queryset = Expense.objects.filter(budget__country__slug=country_params, code=code_params, group=group_params)
    #     for expensive in queryset:
    #         name = expensive.name
    #         year = expensive.budget.year
    #         list_expensive.append({"name": name, "year": year})
    #     return Response(list_expensive)
