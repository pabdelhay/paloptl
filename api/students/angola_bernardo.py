from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.api import BudgetSerializer
from apps.budget.models import Budget, BudgetSummary
from common.methods import get_rates


class AngolaBernardoViewset(ReadOnlyModelViewSet):
    model = Budget
    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()

    @action(detail=False)
    def total_expense(self, request, pk=None):
        year = request.query_params.get('year', 2020)
        base_currency = request.query_params.get('currency', 'USD')
        budgets_per_year = []
        bs = BudgetSummary.objects.filter(budget__year=year)
        rates = get_rates(base_currency)
        for budget_summary in bs:
            rate = rates.get(budget_summary.budget.currency)
            if budget_summary.budget.currency != base_currency:
                if budget_summary.expense_functional_budget:
                    expense_amount = budget_summary.expense_functional_budget / rate
                elif budget_summary.expense_organic_budget:
                    expense_amount = budget_summary.expense_organic_budget / rate
                else:
                    expense_amount = 0

                if budget_summary.revenue_nature_budget:
                    revenue_amount = budget_summary.revenue_nature_budget / rate
                elif budget_summary.revenue_source_budget:
                    revenue_amount = budget_summary.revenue_source_budget / rate
                else:
                    revenue_amount = 0

            else:
                expense_amount = budget_summary.expense_organic_budget
                revenue_amount = budget_summary.revenue_nature_budget

            budgets_per_year.append({
                'country': budget_summary.budget.country.name,
                'expense': expense_amount,
                'revenue': revenue_amount,
                'year': budget_summary.budget.year,
                'group': "functional" if budget_summary.expense_functional_budget else "organic",
                'currency': budget_summary.budget.currency})
        return Response(budgets_per_year)
