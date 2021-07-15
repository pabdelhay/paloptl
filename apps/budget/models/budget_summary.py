from django.db import models
from django.utils.translation import gettext_lazy as _


class BudgetSummary(models.Model):
    """
    Budget's aggregated values inferred from expenses and revenues.
    """
    budget = models.OneToOneField('budget.Budget', verbose_name=_("budget"), on_delete=models.CASCADE,
                                  related_name='summary')

    # Inferred values
    expense_functional_budget = models.FloatField(verbose_name=_("expenses budget on functions"), null=True, blank=True,
                                                editable=False)
    expense_functional_execution = models.FloatField(verbose_name=_("expenses execution on functions"), null=True,
                                                   blank=True, editable=False)
    expense_organic_budget = models.FloatField(verbose_name=_("expenses budget on agencies"), null=True, blank=True,
                                              editable=False)
    expense_organic_execution = models.FloatField(verbose_name=_("expenses execution on agencies"), null=True,
                                                 blank=True, editable=False)
    expense_functional_budget = models.FloatField(verbose_name=_("expenses budget on functions"), null=True, blank=True,
                                                  editable=False)
    expense_functional_execution = models.FloatField(verbose_name=_("expenses execution on functions"), null=True,
                                                     blank=True, editable=False)
    expense_organic_budget = models.FloatField(verbose_name=_("expenses budget on agencies"), null=True, blank=True,
                                               editable=False)
    expense_organic_execution = models.FloatField(verbose_name=_("expenses execution on agencies"), null=True,
                                                  blank=True, editable=False)

    class Meta:
        verbose_name = _("budget aggregated")
        verbose_name_plural = _("budget aggregated values")

    def __str__(self):
        return f"{self.budget_id}"
