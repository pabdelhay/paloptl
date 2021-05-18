from dirtyfields import DirtyFieldsMixin
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class BudgetAccount(MPTTModel, DirtyFieldsMixin):
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

    inferred_values = JSONField(default=dict,
                                help_text=_("inferred values from siblings or descendants"))
    inferred_fields = JSONField(default=dict,
                                help_text=_("fields that were inferred (not originally inputted)"))

    last_update = models.DateTimeField(verbose_name=_("last update"), auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['name',]

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def get_model_name(cls):
        """
        Return model name ('function' or 'agency')
        :return: string
        """
        return cls._meta.model_name

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

    def get_value(self, field):
        """
        Get value from field. If field is not set, fetch value from inferred values.
        :param field: string
        :return: float
        """
        value = getattr(self, field)
        if not value:
            value = self.inferred_values.get(field, None)
        return value

    def infer_aggregated_value(self, field):
        """
        Sum all descendants values from this field. Every descendant MUST have this field set, otherwise raises
        exception.

        return float or None
        """
        descendants_qs = self.get_descendants()
        descendants_count = descendants_qs.count()

        # Try to infer from descendants
        if descendants_count > 0:
            descendants_with_value = descendants_qs.exclude(**{f'{field}__isnull': True}).exists()
            if descendants_with_value:
                # At least one descendants have values set, so we infer from the sum of these values.
                return descendants_qs.aggregate(total=Sum(field))['total']

        # Try to infer from siblings
        if field.endswith('_aggregated'):
            base_field = field.replace("_aggregated", "")
            investment_field = getattr(self, f"{base_field}_investment", None)
            operation_field = getattr(self, f"{base_field}_operation", None)
            if investment_field and operation_field:
                return investment_field + operation_field
            elif investment_field and not operation_field:
                # Case only investment_field was set, we consider aggregated as this value
                return investment_field
            elif operation_field and not investment_field:
                # Case only operation_field was set, we consider aggregated as this value
                return operation_field

        return None

    def update_inferred_values(self):
        """
        Updates the 'inferred_values' json field with values aggregated from siblings or descendants.
        :returns: dict (inferred_values)
        """
        fields = ['budget_investment', 'budget_operation', 'budget_aggregated',
                  'execution_investment', 'execution_operation', 'execution_aggregated']
        self.inferred_values = {}
        for field in fields:
            inferred = self.infer_aggregated_value(field)
            if not inferred:
                continue
            self.inferred_values[field] = inferred

            if not getattr(self, field) or self.inferred_fields.get(field, None):
                # Save the inferred value to it's respective field on instance
                # IF the field is None OR it was filled by a previous inference (overriding inferred field).
                setattr(self, field, inferred)
                self.inferred_fields[field] = True

        self.save()
        return self.inferred_values
