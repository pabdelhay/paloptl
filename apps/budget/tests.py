import copy
import csv

from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management import call_command
from django.test import TestCase

from apps.budget.choices import UploadCategoryChoices, UploadReportChoices, ExpenseGroupChoices
from apps.budget.models import Budget, Upload, Expense
from apps.geo.models import Country


class BudgetAccountTestCase(TestCase):
    def setUp(self):
        call_command('create_countries')
        self.user = User.objects.create(username='user', is_superuser=True)
        self.country = Country.objects.first()
        self.budget = Budget.objects.create(country=self.country, year=2020)

    def test_infer_aggregated_value(self):
        f0 = Expense.objects.create(budget=self.budget, group=ExpenseGroupChoices.FUNCTIONAL,
                                    name="test function", code="f0")
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

        # Test descendants
        f00 = Expense.objects.create(budget=self.budget, group=ExpenseGroupChoices.FUNCTIONAL, name="test subfunction",
                                     code="f00", parent=f0)
        f00.budget_investment = 5
        f00.save()
        f01 = Expense.objects.create(budget=self.budget, group=ExpenseGroupChoices.FUNCTIONAL, name="test subfunction1",
                                     code="f01", parent=f0)
        f01.budget_investment = 6
        f01.save()

        inferred_budget_aggregated = f0.infer_aggregated_value('budget_investment')
        self.assertEqual(inferred_budget_aggregated, 11,
                         msg="Aggregated value should be sum of descendants")

        # Test not possible to infer
        f01.budget_investment = None
        f01.save()
        inferred_budget_aggregated = f0.infer_aggregated_value('budget_investment')
        self.assertEqual(inferred_budget_aggregated, 5,
                         msg="Aggregated value should be sum of descendants, event there are descendants without "
                             "values set.")

    def test_update_inferred_values(self):
        f0 = Expense.objects.create(budget=self.budget, group=ExpenseGroupChoices.FUNCTIONAL, name="test function",
                                    code="f0")
        f0.budget_investment = 10
        f0.budget_operation = 20
        f0.execution_investment = 30
        f0.execution_operation = 40
        f0.save()
        inferred_values = f0.update_inferred_values()

        self.assertEqual(len(inferred_values.keys()), 2, msg="Only two inferred values should be created")

    def test_upload_validate(self):
        upload = Upload(budget=self.budget, category=UploadCategoryChoices.EXPENSE,
                        report=UploadReportChoices.OGE, uploaded_by=self.user)

        header = ['group', 'category_code', 'category', 'subcategory_code', 'subcategory', 'budget_aggregated',
                  'execution_aggregated']

        def write_data_to_file(data):
            file_name = f'budget_test.csv'
            output_file = NamedTemporaryFile(mode='w+')
            writer = csv.DictWriter(output_file, fieldnames=header, delimiter=',')
            writer.writeheader()
            for row in data:
                writer.writerow(row)
            file = File(output_file, name=file_name)
            return file

        # DATA OK
        data_ok = [
            {'group': "organic", 'category_code': 1, 'category': "Category 1",
             'subcategory_code': 'S1', 'subcategory': "Subcategory 1",
             'budget_aggregated': 100, 'execution_aggregated': 70},
            {'group': "organic", 'category_code': 1, 'category': "Category 1",
             'subcategory_code': 'S2', 'subcategory': "Subcategory 2",
             'budget_aggregated': 200, 'execution_aggregated': 150},
        ]

        data = copy.deepcopy(data_ok)
        upload.file = write_data_to_file(data)
        upload.save()
        validation_result = upload.validate()

        self.assertEqual(validation_result, True,
                         msg="Data should be valid.")

        # DATA WITH MULTIPLE CODES FOR SAME SUBCATEGORY
        data[1]['subcategory'] = data[0]['subcategory']
        upload.file = write_data_to_file(data)
        upload.save()
        validation_result = upload.validate()

        self.assertEqual(validation_result, False,
                         msg="Data should not be valid.")
        self.assertEqual(len(upload.errors), 1,
                         msg="There should be only one error.")
        error_msg = str(upload.errors[0].lower())
        msg_is_ok = "different codes for" in error_msg
        self.assertEqual(msg_is_ok, True,
                         msg="Error msg should contain 'different codes for...'")

        # DATA WITH MULTIPLE SUBCATEGORY NAMES FOR SAME CODE
        data = copy.deepcopy(data_ok)
        data[1]['subcategory_code'] = data[0]['subcategory_code']
        upload.file = write_data_to_file(data)
        upload.save()
        validation_result = upload.validate()

        self.assertEqual(validation_result, False,
                         msg="Data should not be valid.")
        error_msg = str(upload.errors[0].lower())
        msg_is_ok = "different names for" in error_msg
        self.assertEqual(msg_is_ok, True,
                         msg="Error msg should contain 'different names for...'")
