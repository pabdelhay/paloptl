from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class BudgetAccount(MPTTModel):
    class TaxonomyLevelsNotSet(Exception):
        pass

    budget = models.ForeignKey('budget.Budget', verbose_name=_("budget"), on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_("name"), max_length=100)
    parent = TreeForeignKey('self', verbose_name=_("parent"), null=True, blank=True, related_name='children',
                            db_index=True, on_delete=models.CASCADE)

    budget_investment = models.FloatField(verbose_name=_("initial budget for investment"), null=True, blank=True)
    budget_operation = models.FloatField(verbose_name=_("initial budget for operation"), null=True, blank=True)
    budget_aggregated = models.FloatField(verbose_name=_("initial budget"), null=True, blank=True)

    execution_investment = models.FloatField(verbose_name=_("execution for investment"), null=True, blank=True)
    execution_operation = models.FloatField(verbose_name=_("execution for operation"), null=True, blank=True)
    execution_aggregated = models.FloatField(verbose_name=_("execution"), null=True, blank=True)

    last_update = models.DateTimeField(verbose_name=_("last update"), auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def get_taxonomy(cls, level=0):
        if not getattr(cls, 'TAXONOMY_LEVELS', None):
            raise cls.TaxonomyLevelsNotSet()
        return cls.TAXONOMY_LEVELS[level]
