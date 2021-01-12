from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class BudgetAccount(MPTTModel):
    class TaxonomyLevelsNotSet(Exception):
        pass

    class NotAllDescendantsHaveValueSet(Exception):
        pass

    budget = models.ForeignKey('budget.Budget', verbose_name=_("budget"), on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_("name"), max_length=255)
    code = models.CharField(verbose_name=_("code"), max_length=20, null=True, blank=True)
    parent = TreeForeignKey('self', verbose_name=_("parent"), null=True, blank=True, related_name='children',
                            db_index=True, on_delete=models.CASCADE)

    initial_budget_investment = models.FloatField(verbose_name=_("initial budget for investment"), null=True, blank=True)
    initial_budget_operation = models.FloatField(verbose_name=_("initial budget for operation"), null=True, blank=True)
    initial_budget_aggregated = models.FloatField(verbose_name=_("initial budget"), null=True, blank=True)

    budget_investment = models.FloatField(verbose_name=_("updated budget for investment"), null=True, blank=True)
    budget_operation = models.FloatField(verbose_name=_("updated budget for operation"), null=True, blank=True)
    budget_aggregated = models.FloatField(verbose_name=_("updated budget"), null=True, blank=True)

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

    def get_taxonomy_label(self):
        return self.get_taxonomy(self.level)

    def get_hierarchy_name(self):
        name = self.name
        if self.parent is not None:
            name = self.parent.name + f" > {name}"
        return name

    def infer_aggregated_value(self, field):
        """
        Sum all descendants values from this field. Every descendant MUST have this field set, otherwise raises
        exception.

        return float or None
        """
        descendants_qs = self.get_descendants()
        descendants_count = descendants_qs.count()
        if not descendants_count:
            return None

        descendants_with_value = descendants_qs.exclude(**{f'{field}__isnull': True}).count()
        if descendants_with_value != descendants_count:
            raise self.NotAllDescendantsHaveValueSet()

        return descendants_qs.aggregate(total=Sum(field))['total']
