from django.utils.translation import gettext_lazy as _

from apps.budget.models.budget_account import BudgetAccount


class Agency(BudgetAccount):
    TAXONOMY_LEVELS = [
        _("agency"),
        _("budget unit")
    ]

    class Meta:
        verbose_name = _("agency")
        verbose_name_plural = _("agencies")
