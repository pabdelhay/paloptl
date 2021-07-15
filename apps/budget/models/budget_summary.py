from django.db import models
from django.utils.translation import gettext_lazy as _


class BudgetSummary(models.Model):
    """
    Budget's aggregated values inferred from expenses and revenues.
    """
    budget = models.OneToOneField('budget.Budget', verbose_name=_("budget"), on_delete=models.CASCADE,
                                  related_name='summary')

    # Inferred values
    expense_functional_budget = models.FloatField(verbose_name=_("expenses budget (functional)"), null=True,
                                                  blank=True, editable=False)
    expense_functional_execution = models.FloatField(verbose_name=_("expenses execution (functional)"), null=True,
                                                     blank=True, editable=False)
    expense_organic_budget = models.FloatField(verbose_name=_("expenses budget (organic)"), null=True, blank=True,
                                               editable=False)
    expense_organic_execution = models.FloatField(verbose_name=_("expenses execution (organic)"), null=True,
                                                  blank=True, editable=False)
    revenue_nature_budget = models.FloatField(verbose_name=_("revenues budget (nature)"), null=True, blank=True,
                                              editable=False)
    revenue_nature_execution = models.FloatField(verbose_name=_("revenues execution (nature)"), null=True,
                                                 blank=True, editable=False)
    revenue_source_budget = models.FloatField(verbose_name=_("revenues budget (source)"), null=True, blank=True,
                                              editable=False)
    revenue_source_execution = models.FloatField(verbose_name=_("revenues execution (source)"), null=True,
                                                 blank=True, editable=False)

    class Meta:
        verbose_name = _("budget summary")
        verbose_name_plural = _("aggregated values")

    def __str__(self):
        return _("Aggregated values for Budget #{}").format(self.budget_id)
