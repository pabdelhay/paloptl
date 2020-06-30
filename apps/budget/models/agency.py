from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.budget.models.budget_account import BudgetAccount


class Agency(BudgetAccount):
    TAXONOMY_LEVELS = [
        _("agency"),
        _("budget unit")
    ]
    budget = models.ForeignKey('budget.Budget', verbose_name=_("budget"), related_name='agencies',
                               on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("agency")
        verbose_name_plural = _("agencies")
