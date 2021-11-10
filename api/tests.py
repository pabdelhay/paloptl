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

    def test_budgets_expenses_revenues(self):
        budget2020 = Budget.objects.create(country=self.country, year=2020)
        budget2019 = Budget.objects.create(country=self.country, year=2019)

        expense2021 = Expense.objects.create(budget=self.budget, group=ExpenseGroupChoices.ORGANIC,
                                             name="JUVENTUDE", code="JV")
        expense2021.budget_investment = 10
        expense2021.budget_operation = 20
        expense2021.execution_investment = 13
        expense2021.execution_operation = 37
        expense2021.save()

        revenue2021 = Revenue.objects.create(budget=self.budget, group=RevenueGroupChoices.NATURE,
                                             name="JUVENTUDE", code="JV")
        revenue2021.budget_investment = 8
        revenue2021.budget_operation = 10
        revenue2021.execution_investment = 18
        revenue2021.execution_operation = 15
        revenue2021.save()

        expense2020 = Expense.objects.create(budget=budget2020, group=ExpenseGroupChoices.FUNCTIONAL,
                                    name="EDUCAÇÂO", code="ED")
        expense2020.budget_investment = 16
        expense2020.budget_operation = 5
        expense2020.execution_investment = 18
        expense2020.execution_operation = 30
        expense2020.save()

        expense2019 = Expense.objects.create(budget=budget2019, group=ExpenseGroupChoices.FUNCTIONAL,
                                             name="DESPORTO", code="SP")
        expense2019.budget_investment = 10
        expense2019.budget_operation = 12
        expense2019.execution_investment = 10
        expense2019.execution_operation = 27
        expense2019.save()

        revenue2020 = Revenue.objects.create(budget=budget2020, group=RevenueGroupChoices.NATURE,
                                    name="EDUCAÇÂO", code="ED")
        revenue2020.budget_investment = 30
        revenue2020.budget_operation = 9
        revenue2020.execution_investment = 8
        revenue2020.execution_operation = 12
        revenue2020.save()

        revenue2019 = Revenue.objects.create(budget=budget2019, group=RevenueGroupChoices.NATURE,
                                             name="DESPORTO", code="SP")
        revenue2019.budget_investment = 22
        revenue2019.budget_operation = 19
        revenue2019.execution_investment = 20
        revenue2019.execution_operation = 15
        revenue2019.save()

        self.budget.update_inferred_values()
        budget2020.update_inferred_values()
        budget2019.update_inferred_values()

        base_url = f'/budgets/expenses_and_revenues/'
        response = self.client.get(self.get_api_url(base_url), {'country': self.country.id})
        r = response.json()

        self.assertEqual('budget_expense' in r[0], True, "Key expense not found.")
        self.assertEqual('budget_revenue' in r[0], True, "Key revenue not found.")
        self.assertEqual('year' in r[0], True, "Key year not found.")

        for budget_summary in r:
            if budget_summary['year'] == 2021:
                self.assertEqual(budget_summary['budget_expense'], (expense2021.budget_investment + expense2021.budget_operation), 'Invalid expense value.')
                self.assertEqual(budget_summary['budget_revenue'], (revenue2021.budget_investment + revenue2021.budget_operation), 'Invalid revenue value.')
            elif budget_summary["year"] == 2020:
                self.assertEqual(budget_summary['budget_expense'],  (expense2020.budget_investment + expense2020.budget_operation),  'Invalid expense value.')
                self.assertEqual(budget_summary['budget_revenue'],  (revenue2020.budget_investment + revenue2020.budget_operation),  'Invalid revenue value.')
            else:
                self.assertEqual(budget_summary['budget_expense'], (expense2019.budget_investment + expense2019.budget_operation),  'Invalid expense value.')
                self.assertEqual(budget_summary['budget_revenue'],  (revenue2019.budget_investment + revenue2019.budget_operation), 'Invalid revenue value.')
