from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.api import BudgetSerializer
from apps.budget.models import Budget, BudgetSummary, Expense


class MocambiqueIlidioViewset(ReadOnlyModelViewSet):
    model = Budget
    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()

    @action(detail=False)
    def year_percent(self, request, pk=None):
        q_budget_summary = BudgetSummary.objects.filter(budget__country__name="Moçambique")

        list_disc = {}
        list_result = []

        for c in q_budget_summary:
            result = {
                "percent": c.expense_functional_execution / c.expense_functional_budget,
                "year": c.budget.year
            }

            list_result.append(result)

            list_disc = list_result

        return Response(list_disc)

    @action(detail=False)
    def year_percent_get_parameter(self, request, pk=None):
        id = request.query_params.get('id')
        q_budget_summary = BudgetSummary.objects.filter(budget__country__id=id)

        list_result = []

        for c in q_budget_summary:
            if c.expense_functional_budget is not None and c.expense_functional_execution is not None:
                result = {
                    "percent": c.expense_functional_execution / c.expense_functional_budget,
                    "year": c.budget.year
                }

                list_result.append(result)
        return Response(list_result)


    @action(detail=False)
    def expense_detail_country(self, request, pk=None):

        group = request.query_params.get('group')
        code = request.query_params.get('code')
        country = request.query_params.get('name')

        q_expense_detail_country = Expense.objects.filter(budget__country__name=country, code=code, group=group)

        # list_disc = {}
        list_result = []

        for c in q_expense_detail_country:
            result = {
                "name": c.budget.country.name,
                "year": c.budget.year,
                "budget_operation": c.budget_operation,
                "budget_investment": c.budget_investment,
                "execution_operation": c.execution_operation,
            }

            list_result.append(result)

            # list_disc = list_result

        return Response(list_result)
