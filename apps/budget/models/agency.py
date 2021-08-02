from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.budget.choices import ExpenseGroupChoices
from apps.budget.models.budget_account import BudgetAccount


class Agency(BudgetAccount):
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
        _("agency"),
        _("budget unit")
    ]
    group = ExpenseGroupChoices.ORGANIC

    budget = models.ForeignKey('budget.Budget', verbose_name=_("budget"), related_name='agencies',
                               on_delete=models.CASCADE)

    upload_logs = GenericRelation('budget.UploadLog', related_query_name='agency')
    migrated_to = GenericRelation('budget.Expense', related_query_name='old_instance')

    class Meta:
        verbose_name = _("agency")
        verbose_name_plural = _("agencies data")
        ordering = ['-budget_aggregated']

    @classmethod
    def get_model_label(cls):
        """
        Return model verbose name
        :return: string
        """
        return "expense - OLD"
