from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.api import BudgetSerializer
from apps.budget.models import Budget, BudgetSummary
from common.students.angola_estima import apply_exchange


class AngolaEstimaViewset(ReadOnlyModelViewSet):
    model = Budget
    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()

    @action(detail=False)
    def summary_budget_per_year_all_country(self, request, pk=None):
        year = request.query_params.get('year', 2018)
        base_currency = request.query_params.get('base_currency')
        aggregate_budgets_summery = []

        # UpGreat code to new
        # Identify an Alteraction to pull

        budget_summerys = BudgetSummary.objects.filter(budget__year=year)

        """ Puchar o as Rates """
        rate = apply_exchange(base_currency)

        for budgetSummery in budget_summerys:
            tupla = {}

            tupla['country'] = budgetSummery.budget.country.name
            tupla[
                'budget'] = budgetSummery.expense_organic_budget if budgetSummery.expense_functional_budget is None else budgetSummery.expense_functional_budget
            tupla['budget_euro'] = budgetSummery.expense_organic_budget / rate.get(
                budgetSummery.budget.currency) if budgetSummery.expense_functional_budget is None else budgetSummery.expense_functional_budget / rate.get(
                budgetSummery.budget.currency)
            tupla['year'] = year
            tupla['source'] = 'Organic' if budgetSummery.expense_functional_budget is None else 'Functional'

            aggregate_budgets_summery.append(tupla)

        return Response(aggregate_budgets_summery)
