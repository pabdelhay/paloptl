from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum
from djmoney.models.fields import CurrencyField

from common.mixins import CountryMixin
from django.utils.translation import gettext_lazy as _


class Budget(CountryMixin, models.Model):
    """
    A (year, country) aggregation of budget data.
    """
    country = models.ForeignKey('geo.Country', verbose_name=_("country"), on_delete=models.CASCADE,
                                related_name='budgets')
    year = models.IntegerField(verbose_name=_("year"))
    currency = CurrencyField(verbose_name=_("currency"), choices=settings.CURRENCY_CHOICES, editable=False,
                             help_text=_("All values from budget presented in this currency"))

    # Inferred values
    function_budget = models.FloatField(verbose_name=_("function's budget"), null=True, blank=True, editable=False)
    function_execution = models.FloatField(verbose_name=_("function's execution"), null=True, blank=True,
                                           editable=False)
    agency_budget = models.FloatField(verbose_name=_("agency's execution"), null=True, blank=True, editable=False)
    agency_execution = models.FloatField(verbose_name=_("agency's execution"), null=True, blank=True, editable=False)

    # TODO: Move to a different model.
    score_open_data = models.SmallIntegerField(verbose_name=_("score - open data"), help_text="0 - 100",
                                               null=True, blank=True, validators=[MinValueValidator(0),
                                                                                  MaxValueValidator(100)])
    score_reports = models.SmallIntegerField(verbose_name=_("score - reports"), help_text="0 - 100",
                                             null=True, blank=True, validators=[MinValueValidator(0),
                                                                                MaxValueValidator(100)])
    score_data_quality = models.SmallIntegerField(verbose_name=_("score - data quality"), help_text="0 - 200",
                                                  null=True, blank=True, validators=[MinValueValidator(0),
                                                                                     MaxValueValidator(200)])
    transparency_index = models.SmallIntegerField(verbose_name=_("transparency index"), help_text="0 - 100",
                                                  null=True, blank=True, validators=[MinValueValidator(0),
                                                                                     MaxValueValidator(100)])

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
        budget_accounts = [self.functions, self.agencies]

        # Set inferred values for budget's Functions and Agencies.
        for budget_account_qs in budget_accounts:
            for budget_account in budget_account_qs.all().order_by('-level'):
                budget_account.update_inferred_values()

        # Set inferred values for Budget (function_budget, function_execution, agency_budget, agency_execution)
        for budget_account_qs in budget_accounts:
            budget_account_prefix = budget_account_qs.model._meta.model_name  # ['agency', 'function']
            budget_account_budget, budget_account_execution = None, None
            for budget_account in budget_account_qs.filter(level=0):
                budget = budget_account.get_value('budget_aggregated')
                execution = budget_account.get_value('execution_aggregated')
                if budget:
                    budget_account_budget = budget_account_budget or 0
                    budget_account_budget += budget
                if execution:
                    budget_account_execution = budget_account_execution or 0
                    budget_account_execution += execution

            setattr(self, f'{budget_account_prefix}_budget', budget_account_budget)
            setattr(self, f'{budget_account_prefix}_execution', budget_account_execution)

        self.save()
