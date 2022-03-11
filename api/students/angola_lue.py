from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.api import BudgetSerializer
from apps.budget.models import Budget, BudgetSummary
from common.students.angola_lupossa import exchange_base_currency, calculator_exchange, data_year_budget


class AngolaLueViewset(ReadOnlyModelViewSet):
    model = Budget
    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()

    @action(detail=False)
    def base_currency(self, request, pk=None):
        year = request.query_params.get("year", 2020)
        base_currency = request.query_params.get("cur", "EUR")
        data = BudgetSummary.objects.filter(budget__year=year)
        rates = exchange_base_currency(base_currency)
        list = []

        for db in data:
            dic = {}
            func = db.expense_functional_budget
            orga = db.expense_organic_budget
            currency = db.budget.currency

            if func is not None:
                dic["country"] = db.budget.country.name
                amount_in_base_currency = calculator_exchange(func, currency, dic, rates, base_currency)
                dic["budget_base_currency_" + base_currency] = amount_in_base_currency
                dic["budget_base_currency"] = amount_in_base_currency
                dic["budget_" + currency] = func
                dic["group"] = "functional"
                dic["year"] = year

            else:
                if orga is not None:
                    dic["country"] = db.budget.country.name
                    amount_in_base_currency = calculator_exchange(orga, currency, dic, rates, base_currency)
                    dic["budget_base_currency_" + base_currency] = amount_in_base_currency
                    dic["budget_base_currency"] = amount_in_base_currency
                    dic["budget_" + currency] = orga
                    dic["group"] = "organic"
                    dic["year"] = year

            if bool(dic):
                list.append(dic)

        return Response(list)

    @action(detail=False)
    def palop_base_currency(self, request, pk=None):

        base_currency = request.query_params.get("cur", "EUR")
        big_data = BudgetSummary.objects.filter()
        rates = exchange_base_currency(base_currency)
        list = []
        dic_year = {}

        for db in big_data:
            dic_year[db.budget.year] = db.budget.year

        for year in dic_year:

            data = BudgetSummary.objects.filter(budget__year=dic_year[year])
            dic = {}
            dic_country_budget = {}
            total_budget_year = data_year_budget(data, dic_country_budget, rates, base_currency)
            dic["palop_budget_base_currency_" + base_currency] = total_budget_year
            dic["palop_budget_base_currency"] = total_budget_year
            dic["year"] = dic_year[year]

            for key_country in dic_country_budget:
                dic[f"palop_{key_country}_budget_percentage"] = 100 * dic_country_budget[
                    key_country] / total_budget_year

            list.append(dic)

        return Response(list)
