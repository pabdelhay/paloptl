from django.core.management import call_command
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.budget.models import Budget, Function
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
            f0 = Function.objects.create(budget=budget, name="test function", code="f0")
            f0.save()

            f1 = Function.objects.create(parent=f0, budget=budget, name="test sub-function", code="f1")
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

        response = self.client.get(self.get_api_url(base_url), {'budget_account': 'functions'})

        r = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Wrong status code response")

        self.assertEqual(r['name'], self.country.name,
                         "Name of historical on top level should be the name of the country.")
        self.assertEqual(r['data'][0]['year'], '2017',
                         "First historical data should be from 2017's budget.")
        self.assertEqual(r['data'][0]['budget_aggregated'], 20, "Budget aggregated should be 20.")
        self.assertEqual(r['data'][0]['execution_aggregated'], 20, "Execution aggregated should be 20.")
