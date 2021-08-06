import json
import os

import requests
import unicodecsv as csv
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import CurrencyField
from rest_framework import serializers

from apps.budget.choices import UploadStatusChoices, ExpenseGroupChoices, RevenueGroupChoices, UploadCategoryChoices, \
    GROUP_CHOICES_BY_BUDGET_ACCOUNT
from common.mixins import CountryMixin


class Budget(CountryMixin, models.Model):
    """
    A (year, country) aggregation of budget data.
    """
    country = models.ForeignKey('geo.Country', verbose_name=_("country"), on_delete=models.CASCADE,
                                related_name='budgets')
    year = models.IntegerField(verbose_name=_("year"))
    currency = CurrencyField(verbose_name=_("currency"), choices=settings.CURRENCY_CHOICES, editable=False,
                             help_text=_("All values from budget presented in this currency"))
    is_active = models.BooleanField(verbose_name=_("active"), default=True,
                                    help_text=_("This budget will only be included on site if this option is checked."))

    # DEPRECATED since 2021-07-15. TODO: Remove after data migration to above fields.
    function_budget = models.FloatField(verbose_name=_("function's budget"), null=True, blank=True, editable=False)
    function_execution = models.FloatField(verbose_name=_("function's execution"), null=True, blank=True,
                                           editable=False)
    agency_budget = models.FloatField(verbose_name=_("agency's execution"), null=True, blank=True, editable=False)
    agency_execution = models.FloatField(verbose_name=_("agency's execution"), null=True, blank=True, editable=False)

    # CSV file
    output_file = models.FileField(upload_to='exports', null=True, blank=True, editable=False,
                                   help_text=_("Auto generated CSV file with all data from budget."))

    class Meta:
        verbose_name = _("budget")
        verbose_name_plural = _("budgets")
        unique_together = ('country', 'year')
        ordering = ['country', '-year']

    def __str__(self):
        return f"{self.country.name} - {self.year}"

    def save(self, *args, **kwargs):
        is_new = not self.pk
        if is_new:
            self.currency = self.country.currency
        super().save(*args, **kwargs)

    def get_aggregated_data(self, budget_account_model):
        """
        Return sum of budget_aggregated and execution_aggregated values for this Budget.
        :param budget_account_model: model [budget.Agency, budget.Function]
        :return: {'budget': Decimal, 'execution': Decimal}
        """
        qs = budget_account_model.objects.filter(level=0).aggregate(budget=Sum('budget_aggregated'),
                                                                    execution=Sum('budget_execution'))
        return qs

    def update_inferred_values(self):
        """
        Updates all budget inferred values.
        """
        from .budget_summary import BudgetSummary
        budget_accounts = [self.expenses, self.revenues]

        # Set inferred values for budget's expenses and revenues.
        for budget_account_qs in budget_accounts:
            for budget_account in budget_account_qs.all().order_by('-level'):
                budget_account.update_inferred_values()

        # Set inferred values for BudgetAggregated
        budget_summary, created = BudgetSummary.objects.get_or_create(budget=self)
        for budget_account_qs in budget_accounts:
            category_prefix = budget_account_qs.model._meta.model_name  # ['expense', 'revenue']
            group_choices = budget_account_qs.model.group.field.choices  # [ExpenseGroupChoices, RevenueGroupChoices]
            for group, group_label in group_choices:
                budget_account_budget, budget_account_execution = None, None
                for budget_account in budget_account_qs.filter(group=group, level=0):
                    budget = budget_account.get_value('budget_aggregated')
                    execution = budget_account.get_value('execution_aggregated')
                    if budget:
                        budget_account_budget = budget_account_budget or 0
                        budget_account_budget += budget
                    if execution:
                        budget_account_execution = budget_account_execution or 0
                        budget_account_execution += execution

                setattr(budget_summary, f'{category_prefix}_{group}_budget', budget_account_budget)
                setattr(budget_summary, f'{category_prefix}_{group}_execution', budget_account_execution)

        budget_summary.save()

    def update_json_files(self):
        """
        Get data from ['/budgets/{id}/expenses/?group={group}', '/budgets/{id}/revenues/?group={group}'] and create
        a json file for cache with the following name format.
            {country}_{budget_account[expenses/revenues]}_{group}_{year}.json
            eg.:
                angola_expenses_functional_2020.json
                angola_expenses_organic_2020.json
                angola_revenues_nature_2020.json
                angola_revenues_source_2020.json
        """
        groups_dict = {
            'expense': ExpenseGroupChoices,
            'revenue': RevenueGroupChoices
        }
        budget_accounts = [self.expenses, self.revenues]
        for budget_account_qs in budget_accounts:
            budget_account_name = budget_account_qs.model._meta.model_name  # ['expense', 'revenue']
            budget_account_name_for_api = f'{budget_account_name}s'
            groups = groups_dict[budget_account_name]
            for group in groups:
                file_name = f'{self.country.slug}_{budget_account_name_for_api}_{group}_{self.year}.json'
                file_path = os.path.join('budgets', file_name)
                url = f'{settings.SITE_URL}api/budgets/{self.id}/{budget_account_name_for_api}/?group={group}'
                with default_storage.open(file_path, 'w') as outfile:
                    response = requests.get(url)
                    data = response.json()
                    json.dump(data, outfile)

    def update_csv_file(self):
        """
        Create a CSV file with all data from budget.
        Fields are defined on the in-class BudgetCSVSerializer.
        Save csv_file to Budget.output_file.
        """
        class BudgetCSVSerializer(serializers.Serializer):
            budget_type = serializers.CharField(allow_null=True)
            group = serializers.CharField(allow_null=True)
            category = serializers.CharField(allow_null=True)
            category_code = serializers.CharField(required=False, allow_null=True)
            subcategory = serializers.CharField(required=False, allow_null=True)
            subcategory_code = serializers.CharField(required=False, allow_null=True)
            budget_investment = serializers.FloatField(required=False)
            budget_operation = serializers.FloatField(required=False)
            budget_aggregated = serializers.FloatField(required=False)
            execution_investment = serializers.FloatField(required=False)
            execution_operation = serializers.FloatField(required=False)
            execution_aggregated = serializers.FloatField(required=False)

        budget_accounts = {
            'expenses': 'expense',
            'revenues': 'revenue'
        }
        header = list(BudgetCSVSerializer._declared_fields.keys())

        file_name = f'budget_{self.country.slug}_{self.year}.csv'
        output_file = NamedTemporaryFile(mode='wb+')
        writer = csv.DictWriter(output_file, fieldnames=header, delimiter=',')
        writer.writeheader()

        for budget_account, budget_type in budget_accounts.items():
            category_set = getattr(self, budget_account)
            for category in category_set.all().order_by('group', 'tree_id', 'lft',):
                category_name = category.name
                category_code = category.code
                subcategory_name = None
                subcategory_code = None
                if category.level == 1:
                    category_name = category.parent.name
                    category_code = category.parent.code
                    subcategory_name = category.name
                    subcategory_code = category.code
                data = {
                    'budget_type': budget_type,
                    'category': category_name,
                    'category_code': category_code,
                    'subcategory': subcategory_name,
                    'subcategory_code': subcategory_code
                }
                for h in header:
                    value = getattr(category, h, None)
                    if not value:
                        continue
                    data[h] = value
                serializer = BudgetCSVSerializer(data=data)
                serializer.is_valid()
                serializer_data = serializer.validated_data
                writer.writerow(serializer_data)

        self.output_file.delete()  # To override file instead of creating another file with different name.
        self.output_file = File(output_file, name=file_name)
        self.save()

        output_file.close()
        return output_file

    def has_in_progress_upload(self):
        return self.uploads.filter(status__in=UploadStatusChoices.get_in_progress_status()).count() > 0

    def has_waiting_reimport_uploads(self):
        return self.uploads.filter(status=UploadStatusChoices.WAITING_REIMPORT).count() > 0

    def get_available_budget_accounts(self):
        summary = self.summary
        available_budget_accounts = []
        for budget_type, label_budget_type in UploadCategoryChoices.choices:
            group_choices = GROUP_CHOICES_BY_BUDGET_ACCOUNT[budget_type].choices
            for group, label_group in group_choices:
                budget = getattr(summary, f'{budget_type}_{group}_budget', None)
                execution = getattr(summary, f'{budget_type}_{group}_execution', None)
                if budget or execution:
                    available_budget_accounts.append(f'{budget_type}s')
                    continue
        return available_budget_accounts

    def get_available_groups(self):
        summary = self.summary
        available_groups = []
        for budget_type, label_budget_type in UploadCategoryChoices.choices:
            group_choices = GROUP_CHOICES_BY_BUDGET_ACCOUNT[budget_type].choices
            for group, label_group in group_choices:
                budget = getattr(summary, f'{budget_type}_{group}_budget', None)
                execution = getattr(summary, f'{budget_type}_{group}_execution', None)
                if budget or execution:
                    available_groups.append(group)
        return available_groups
