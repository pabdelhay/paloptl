from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.budget.choices import RevenueGroupChoices
from apps.budget.models.budget_account import BudgetAccount


class Revenue(BudgetAccount):
    TAXONOMY_LEVELS_BY_GROUP = {
        RevenueGroupChoices.NATURE: [
            _("nature"),
            _("nature sub-group")
        ],
        RevenueGroupChoices.SOURCE: [
            _("source"),
            _("source sub-group")
        ]
    }

    budget = models.ForeignKey('budget.Budget', verbose_name=_("budget"), related_name='revenues',
                               on_delete=models.CASCADE)
    group = models.CharField(verbose_name=_("group"), max_length=30, choices=RevenueGroupChoices.choices)

    class Meta:
        verbose_name = _("revenue")
        verbose_name_plural = _("revenues")
        ordering = ['-budget_aggregated']
