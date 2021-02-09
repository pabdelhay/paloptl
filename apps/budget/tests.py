from django.core.management import call_command
from django.test import TestCase


# Create your tests here.
from apps.budget.models import Budget, Function
from apps.geo.models import Country


class BudgetAccountTestCase(TestCase):
    def setUp(self):
        call_command('create_countries')
        self.country = Country.objects.first()
        self.budget = Budget.objects.create(country=self.country, year=2020)

    def test_infer_aggregated_value(self):
        f0 = Function.objects.create(budget=self.budget, name="test function", code="f0")
        f0.budget_investment = 10
        f0.budget_operation = 20
        f0.execution_investment = 30
        f0.execution_operation = 40
        f0.save()

        # Test sibling
        inferred_budget_aggregated = f0.infer_aggregated_value('budget_aggregated')
        self.assertEqual(inferred_budget_aggregated, 30,
                         msg="Aggregated value should be sum of siblings")

        # Test sibling
        inferred_budget_aggregated = f0.infer_aggregated_value('execution_aggregated')
        self.assertEqual(inferred_budget_aggregated, 70,
                         msg="Aggregated value should be sum of siblings")

        # Test sibling
        f0.budget_investment = 10
        f0.budget_aggregated = 30
        f0.budget_operation = None
        f0.save()
        inferred_budget_operation = f0.infer_aggregated_value('budget_operation')
        self.assertEqual(inferred_budget_operation, 20,
                         msg="Operation value should be aggregated - investment")

        # Test descendants
        f00 = Function.objects.create(budget=self.budget, name="test subfunction", code="f00", parent=f0)
        f00.budget_investment = 5
        f00.save()
        f01 = Function.objects.create(budget=self.budget, name="test subfunction1", code="f01", parent=f0)
        f01.budget_investment = 6
        f01.save()

        inferred_budget_aggregated = f0.infer_aggregated_value('budget_investment')
        self.assertEqual(inferred_budget_aggregated, 11,
                         msg="Aggregated value should be sum of descendants")

        # Test not possible to infer
        f01.budget_investment = None
        f01.save()
        inferred_budget_aggregated = f0.infer_aggregated_value('budget_investment')
        self.assertEqual(inferred_budget_aggregated, None,
                         msg="If not all descendants have values, and cannot infer from siblings, "
                             "aggregated value should be None")

    def test_update_inferred_values(self):
        f0 = Function.objects.create(budget=self.budget, name="test function", code="f0")
        f0.budget_investment = 10
        f0.budget_operation = 20
        f0.execution_investment = 30
        f0.execution_operation = 40
        f0.save()
        inferred_values = f0.update_inferred_values()

        self.assertEqual(len(inferred_values.keys()), 2, msg="Only two inferred values should be created")
