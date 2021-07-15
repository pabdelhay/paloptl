from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.budget.choices import ExpenseGroupChoices
from apps.budget.models.budget_account import BudgetAccount


class Expense(BudgetAccount):
    TAXONOMY_LEVELS_BY_GROUP = {
        ExpenseGroupChoices.FUNCTIONAL: [
            _("function"),
            _("sub-function")
        ],
        ExpenseGroupChoices.ORGANIC: [
            _("agency"),
            _("budget unit")
        ]
    }

    budget = models.ForeignKey('budget.Budget', verbose_name=_("budget"), related_name='expenses',
                               on_delete=models.CASCADE)
    group = models.CharField(verbose_name=_("group"), max_length=30, choices=ExpenseGroupChoices.choices)

    class Meta:
        verbose_name = _("expense")
        verbose_name_plural = _("expenses")
        ordering = ['-budget_aggregated']
