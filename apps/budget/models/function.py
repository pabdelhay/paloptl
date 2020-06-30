from django.utils.translation import gettext_lazy as _

from apps.budget.models.budget_account import BudgetAccount


class Function(BudgetAccount):
    TAXONOMY_LEVELS = [
        _("function"),
        _("sub-function")
    ]

    class Meta:
        verbose_name = _("function")
        verbose_name_plural = _("functions")
