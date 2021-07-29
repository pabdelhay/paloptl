from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.budget.choices import ExpenseGroupChoices
from apps.budget.models import UploadLog
from apps.budget.models.budget_account import BudgetAccount


class Function(BudgetAccount):
    # For migrations
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

    TAXONOMY_LEVELS = [
        _("function"),
        _("sub-function")
    ]
    group = ExpenseGroupChoices.FUNCTIONAL

    budget = models.ForeignKey('budget.Budget', verbose_name=_("budget"), related_name='functions',
                               on_delete=models.CASCADE)

    upload_logs = GenericRelation('budget.UploadLog', related_query_name='function')
    migrated_to = GenericRelation('budget.Expense', related_query_name='old_instance')

    class Meta:
        verbose_name = _("function")
        verbose_name_plural = _("functional data")
        ordering = ['-budget_aggregated']

    @classmethod
    def get_model_label(cls):
        """
        Return model verbose name
        :return: string
        """
        return "expense - OLD"