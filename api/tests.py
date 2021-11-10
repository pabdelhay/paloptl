from random import random

from django.core.management import call_command
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.budget.choices import ExpenseGroupChoices, CategoryGroupChoices, UploadCategoryChoices, RevenueGroupChoices
from apps.budget.models import Budget, Expense, Category, CategoryMap, Revenue
from apps.geo.models import Country


class APITestCase(TestCase):
    def setUp(self):
        call_command('create_countries')
        self.country = Country.objects.first()
        self.budget = Budget.objects.create(country=self.country, year=2021)
        self.client = APIClient()

    def get_api_url(self, path):
        return f'/api{path}'

    def test_budget_historical(self):
        def create_functions(budget):
            f0 = Expense.objects.create(budget=budget, group=ExpenseGroupChoices.FUNCTIONAL, name="test function",
                                        code="f0")
            f0.save()

            f1 = Expense.objects.create(parent=f0, group=ExpenseGroupChoices.FUNCTIONAL, budget=budget,
                                        name="test sub-function", code="f1")
            f1.budget_investment = 10
            f1.budget_operation = 10
            f1.execution_investment = 10
            f1.execution_operation = 10
            f1.save()

            # Will generate on inferred_values: budget_aggregated=20, execution_aggregated=20
            budget.update_inferred_values()

        budget_2020 = Budget.objects.create(country=self.country, year=2020)
        budget_2019 = Budget.objects.create(country=self.country, year=2019)
        budget_2018 = Budget.objects.create(country=self.country, year=2018)
        budget_2017 = Budget.objects.create(country=self.country, year=2017)

        create_functions(budget_2020)
        create_functions(budget_2019)
        create_functions(budget_2018)
        create_functions(budget_2017)

        base_url = f'/budgets/{budget_2020.id}/historical/'

        response = self.client.get(self.get_api_url(base_url), {'group': ExpenseGroupChoices.FUNCTIONAL,
                                                                'budget_account': 'expenses'})

        r = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Wrong status code response")

        self.assertEqual(r['name'], self.country.name,
                         "Name of historical on top level should be the name of the country.")
        self.assertEqual(r['data'][0]['year'], '2017',
                         "First historical data should be from 2017's budget.")
        self.assertEqual(r['data'][0]['budget_aggregated'], 20, "Budget aggregated should be 20.")
        self.assertEqual(r['data'][0]['execution_aggregated'], 20, "Execution aggregated should be 20.")

        sub_function = Expense.objects.filter(level=1).last()
        response = self.client.get(self.get_api_url(base_url), {'group': ExpenseGroupChoices.FUNCTIONAL,
                                                                'budget_account': 'expenses',
                                                                'budget_account_id': sub_function.id})
        r = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Wrong status code response")
        self.assertEqual(r['name'], sub_function.name,
                         "Name of historical on sub level should be the name of the function.")
        self.assertEqual(r['data'][0]['year'], '2017',
                         "First historical data should be from 2017's budget.")
        self.assertEqual(r['data'][0]['budget_aggregated'], 20, "Budget aggregated should be 20.")
        self.assertEqual(r['data'][0]['execution_aggregated'], 20, "Execution aggregated should be 20.")

    def test_budgets_expense_by_country(self):
        def create_functions(budget):
            f0 = Expense.objects.create(budget=budget, group=ExpenseGroupChoices.FUNCTIONAL,
                                        name="SAUDE", code="SA")
            f0.budget_investment = 5
            f0.budget_operation = 15
            f0.save()

            f1 = Expense.objects.create(budget=budget, group=ExpenseGroupChoices.FUNCTIONAL,
                                        name="EDUCAÇÂO", code="ED")
            f1.budget_investment = 10
            f1.budget_operation = 20
            f1.save()

            f2 = Expense.objects.create(group=ExpenseGroupChoices.FUNCTIONAL, budget=budget,
                                        name="SEGURANÇA", code="SE")
            f2.budget_investment = 8
            f2.budget_operation = 5
            f2.save()

            # Will generate on inferred_values: budget_aggregated=20, execution_aggregated=20
            budget.update_inferred_values()

        budget_2020 = Budget.objects.create(country=self.country, year=2020)
        budget_2019 = Budget.objects.create(country=self.country, year=2019)
        budget_2018 = Budget.objects.create(country=self.country, year=2018)
        budget_2017 = Budget.objects.create(country=self.country, year=2017)

        create_functions(self.budget)
        create_functions(budget_2020)
        create_functions(budget_2019)
        create_functions(budget_2018)
        create_functions(budget_2017)

        saude = Category.objects.create(name="SAUDE", group=CategoryGroupChoices.FUNCTIONAL,
                                        type=UploadCategoryChoices.EXPENSE)
        saude.save()

        educacao = Category.objects.create(name="EDUCAÇÂO", group=CategoryGroupChoices.FUNCTIONAL,
                                           type=UploadCategoryChoices.EXPENSE)
        educacao.save()

        seguranca = Category.objects.create(name="SEGURANÇA", group=CategoryGroupChoices.FUNCTIONAL,
                                            type=UploadCategoryChoices.EXPENSE)
        seguranca.save()

        categories = []
        categories.append(saude.name)
        categories.append(educacao.name)
        categories.append(seguranca.name)

        categoryMap0 = CategoryMap.objects.create(code="SA", country=self.country,
                                                  category=saude)
        categoryMap0.save()

        categoryMap1 = CategoryMap.objects.create(code="ED", country=self.country,
                                                  category=educacao)
        categoryMap1.save()

        categoryMap2 = CategoryMap.objects.create(code="SE", country=self.country,
                                                  category=seguranca)
        categoryMap2.save()

        base_url = f'/budgets/expense_by_country/'

        response = self.client.get(self.get_api_url(base_url), {'year': '2021'})

        r = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         "Wrong status code response")
        self.assertEqual(r['category'].sort(), categories.sort(),
                         "List of category must be equal")
        self.assertEqual(r["data"][0]["country"], "Angola",
                         "Country must be Angola")

        expense_functional_budget = self.budget.summary.expense_functional_budget
        saudepercentage = (20 / expense_functional_budget) * 100
        self.assertEqual(r["data"][0]["SAUDE"], saudepercentage, "SAUDE musta be equal")
        educacaopercentage = (30 / expense_functional_budget) * 100
        self.assertEqual(r["data"][0]["EDUCAÇÂO"], educacaopercentage, "EDUCAÇÂO musta be equal")
        segurancapercentage = (13 / expense_functional_budget) * 100
        self.assertEqual(r["data"][0]["SEGURANÇA"], segurancapercentage, "SEGURANÇA musta be equal")

    def test_expenses_revenue_year_by_country(self):
        self.assertEqual(1, 1, msg="Hello Word Test")

        def create_budget(country, year):
            return Budget.objects.create(country=country, year=year)

        def create_expenses_or_revenue(group, budget):
            if group == ExpenseGroupChoices.FUNCTIONAL:
                e_or_r = Expense.objects.create(group=group, budget=budget, name="test function", code="f0")
                e_or_r.budget_investment = 8
                e_or_r.budget_operation = 17
                e_or_r.save()
            else:
                e_or_r = Revenue.objects.create(group=group, budget=budget, name="test natural", code="f0")
                e_or_r.budget_investment = 16
                e_or_r.budget_operation = 15
                e_or_r.save()

            budget.update_inferred_values()

        budget2020 = create_budget(self.country, "2020")
        budget2019 = create_budget(self.country, "2019")
        budget2018 = create_budget(self.country, "2018")
        budget2017 = create_budget(self.country, "2017")
        budget2016 = create_budget(self.country, "2016")
        budget2015 = create_budget(self.country, "2015")
        budget2014 = create_budget(self.country, "2014")

        create_expenses_or_revenue(ExpenseGroupChoices.FUNCTIONAL, self.budget)
        create_expenses_or_revenue(RevenueGroupChoices.NATURE, self.budget)

        create_expenses_or_revenue(ExpenseGroupChoices.FUNCTIONAL, budget2020)
        create_expenses_or_revenue(RevenueGroupChoices.NATURE, budget2020)

        create_expenses_or_revenue(ExpenseGroupChoices.FUNCTIONAL, budget2019)
        create_expenses_or_revenue(RevenueGroupChoices.NATURE, budget2019)

        create_expenses_or_revenue(ExpenseGroupChoices.FUNCTIONAL, budget2018)
        create_expenses_or_revenue(RevenueGroupChoices.NATURE, budget2018)

        create_expenses_or_revenue(ExpenseGroupChoices.FUNCTIONAL, budget2017)
        create_expenses_or_revenue(RevenueGroupChoices.NATURE, budget2017)

        create_expenses_or_revenue(ExpenseGroupChoices.FUNCTIONAL, budget2016)
        create_expenses_or_revenue(RevenueGroupChoices.NATURE, budget2016)

        create_expenses_or_revenue(ExpenseGroupChoices.FUNCTIONAL, budget2015)
        create_expenses_or_revenue(RevenueGroupChoices.NATURE, budget2015)

        create_expenses_or_revenue(ExpenseGroupChoices.FUNCTIONAL, budget2014)
        create_expenses_or_revenue(RevenueGroupChoices.NATURE, budget2014)

        last_budget = Budget.objects.order_by("-year").last()
        last_budget_expense = Expense.objects.filter(budget=last_budget).last()
        last_budget_revenue = Revenue.objects.filter(budget=last_budget).last()

        last_budget_expense.budget_investment += 2
        last_budget_expense.budget_operation += 2
        last_budget_expense.save()

        last_budget_revenue.budget_operation += 2
        last_budget_revenue.budget_operation += 2
        last_budget_revenue.save()

        last_budget.update_inferred_values()

        base_url = f"/budgets/expenses_revenue_year_by_country/"
        result = self.client.get(self.get_api_url(base_url), {"country": self.country.id})

        result_json = result.json()
        self.assertEqual(len(result_json), 8, msg="Row number returned was not expected")

        first = result_json[0]
        self.assertTrue(isinstance(first["revenue"], float), msg="Expected type is a float")
        self.assertTrue(isinstance(first["expense"], float), msg="Expected type is a float")
        self.assertTrue(isinstance(first["year"], int), msg="Expected type is a int")

        self.assertEqual(len(first), 5, msg="Is not returning the expected number of keys")

        self.assertTrue("revenue" in first, msg="Did not find the corresponding key")
        self.assertTrue("expense" in first, msg="Did not find the corresponding key")
        self.assertTrue("year" in first, msg="Did not find the corresponding key")

        self.assertEqual(result_json[0]["expense"], 25, msg="Unexpected line number")
        self.assertEqual(result_json[0]["revenue"], 31, msg="Unexpected line number")

        self.assertEqual(result_json[-1]["expense"], 29, msg="Unexpected line number")
        self.assertEqual(result_json[-1]["revenue"], 35, msg="Unexpected line number")
