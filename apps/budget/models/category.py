from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.budget.choices import CategoryGroupChoices
from apps.budget.choices import UploadCategoryChoices


class Category(models.Model):
    """
    The Category comparable per country
    """
    name = models.CharField(verbose_name=_("name"), max_length=150)

    group = models.CharField(verbose_name=_("group"), max_length=30, choices=CategoryGroupChoices.choices)

    type = models.CharField(verbose_name=_("type"), max_length=30, choices=UploadCategoryChoices.choices)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        unique_together = ('name', 'group', 'type')
        ordering = ['name']
