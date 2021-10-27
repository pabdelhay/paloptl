from django.core.management import call_command
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.budget.choices import ExpenseGroupChoices
from apps.budget.models import Budget, Expense, Category, CategoryMap
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

    def test_budgets_expenses_by_country(self):
        country_angola = Country.objects.get(slug="angola")
        country_cabo_verde = Country.objects.get(slug="cabo-verde")
        # create budgets
        budget_angola_2020 = Budget.objects.create(country=country_angola, year=2020)
        budget_angola_2019 = Budget.objects.create(country=country_angola, year=2019)
        budget_cabo_verde_2020 = Budget.objects.create(country=country_cabo_verde, year=2020)

        # Health
        Expense.objects.create(budget=budget_angola_2020, group=ExpenseGroupChoices.FUNCTIONAL,
                                              name="Saúde", code="SA", budget_aggregated="30")
        Expense.objects.create(budget=budget_angola_2019, group=ExpenseGroupChoices.FUNCTIONAL,
                                              name="Saúde", code="SA", budget_aggregated="30")

        Expense.objects.create(budget=budget_cabo_verde_2020, group=ExpenseGroupChoices.FUNCTIONAL,
                                                     name="Saúde", code="SA", budget_aggregated="30")
        # Education
        Expense.objects.create(budget=budget_angola_2020, group=ExpenseGroupChoices.FUNCTIONAL,
                                              name="Educação", code="ED", budget_aggregated="30")
        Expense.objects.create(budget=budget_angola_2019, group=ExpenseGroupChoices.FUNCTIONAL,
                                              name="Educação", code="ED", budget_aggregated="50")
        Expense.objects.create(budget=budget_cabo_verde_2020, group=ExpenseGroupChoices.FUNCTIONAL,
                               name="Educação", code="ED", budget_aggregated="50")
        # Security
        Expense.objects.create(budget=budget_angola_2020, group=ExpenseGroupChoices.FUNCTIONAL,
                                              name="Segurança", code="SE", budget_aggregated="40")
        Expense.objects.create(budget=budget_angola_2019, group=ExpenseGroupChoices.FUNCTIONAL,
                                              name="Segurança", code="SE", budget_aggregated="20")
        Expense.objects.create(budget=budget_cabo_verde_2020, group=ExpenseGroupChoices.FUNCTIONAL,
                               name="Segurança", code="SE", budget_aggregated="20")
        # Create categories and categories maps
        category_health = Category.objects.create(name="Saúde", type="expense", group="functional")
        category_education = Category.objects.create(name="Educação", type="expense", group="functional")
        category_security = Category.objects.create(name="Segurança", type="expense", group="functional")
        # Create Category Maps
        CategoryMap.objects.create(code="SA", country=country_angola, category=category_health)
        CategoryMap.objects.create(code="ED", country=country_angola, category=category_education)
        CategoryMap.objects.create(code="SE", country=country_angola, category=category_security)
        CategoryMap.objects.create(code="SA", country=country_cabo_verde, category=category_health)
        CategoryMap.objects.create(code="ED", country=country_cabo_verde, category=category_education)
        CategoryMap.objects.create(code="SE", country=country_cabo_verde, category=category_security)
        # Call budgets update_values
        budget_angola_2020.update_inferred_values()
        budget_angola_2019.update_inferred_values()
        budget_cabo_verde_2020.update_inferred_values()
        # Call to API
        base_url = '/budgets/expenses_by_country/'
        response = self.client.get(self.get_api_url(base_url), {'year': 2020})
        r = response.json()
        # Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Wrong status code response")
        self.assertEqual(r['data'][0]['country'], "Angola", "return of data should be ordered by name")
        self.assertEqual(r['data'][0]['Educação'], 30, "Percentage of education should be 30")
        self.assertEqual(r['data'][0]['Saúde'], 30, "Percentage of health should be 30")
        self.assertEqual(r['data'][0]['Segurança'], 40, "Percentage of security should be 40")
        self.assertEqual(r['data'][1]['country'], "Cabo Verde", "return of data should be ordered by name")
        self.assertEqual(r['data'][1]['Educação'], 50, "Percentage of education should be 50")
        self.assertEqual(r['data'][1]['Saúde'], 30, "Percentage of health should be 30")
        self.assertEqual(r['data'][1]['Segurança'], 20, "Percentage of security should be 20")