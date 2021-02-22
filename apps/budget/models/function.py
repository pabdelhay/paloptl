from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.budget.models.budget_account import BudgetAccount


class Function(BudgetAccount):
    TAXONOMY_LEVELS = [
        _("function"),
        _("sub-function")
    ]
    budget = models.ForeignKey('budget.Budget', verbose_name=_("budget"), related_name='functions',
                               on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("function")
        verbose_name_plural = _("functional data")
        ordering = ['-budget_aggregated']
