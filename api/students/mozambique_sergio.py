from pdb import Restart

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.api import BudgetSerializer
from apps.budget.models import Budget, BudgetSummary,Expense
from common.methods import get_rates


class MozambiqueSergioViewset(ReadOnlyModelViewSet):
    model = Budget
    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()

    @action(detail=False)
    def hello_palop(self, request, pk=None):
        slug = request.query_params.get('slug')
        budgets_per_year = []
        expenses = BudgetSummary.objects.filter(budget__country__slug=slug).order_by('-budget__year')

        for pe in expenses:
            budgets_per_year.append({
                'percent': pe.expense_functional_execution / pe.expense_functional_budget,
                'year': pe.budget.year,
            })
            # print( f"{int((pe.expense_functional_execution * 100) / pe.expense_functional_budget)}{'% - '}{pe.budget.year}")

        return Response(budgets_per_year)

    @action(detail=False)
    def expenses_per_year_slug_group(self, request, pk=None):
        slug = request.query_params.get('slug')
        group = request.query_params.get('group')
        code = request.query_params.get('code')
        expenses_per_year_slug_group = []

        expenses = Expense.objects.filter(code=code, budget__country__slug=slug, group=group).order_by(
            '-budget__year')

        for pe in expenses:
            expenses_per_year_slug_group.append({

                'year': f"{pe.budget.year}",
                'budget_operation': pe.budget_operation,
                'budget_investment': pe.budget_investment,
                # float(f"{format((pe.budget_operation / (pe.budget_operation + pe.budget_investment)) * 100, '.2f')}"),
                # 'budget_investment': float(
                # f"{format((pe.budget_investment / (pe.budget_operation + pe.budget_investment)) * 100, '.2f')}"),
                'execution_operation': pe.execution_operation,
                'execution_investment': pe.execution_investment,
                'name': pe.name,




            })


        return Response(expenses_per_year_slug_group)

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
                'expense_group': "functional" if budget_summary.expense_functional_budget else "organic",
                'revenue_group': "nature" if budget_summary.revenue_nature_budget else "source",
                'currency': budget_summary.budget.currency})
        return Response(budgets_per_year)
