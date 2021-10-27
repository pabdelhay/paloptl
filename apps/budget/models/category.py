from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.budget.choices import CategoryGroupChoice, UploadCategoryChoices


class Category(models.Model):

    name = models.CharField(verbose_name=_("name"), max_length=255)
    type = models.CharField(verbose_name=_("type"), max_length=30, choices=UploadCategoryChoices.choices)
    group = models.CharField(verbose_name=_("group"), max_length=30, choices=CategoryGroupChoice.choices)

    def __str__(self):
        return f'{self.name} - {self.type} - {self.group}'

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        unique_together = ('name', 'type', 'group')
        ordering = ['name', 'type', 'group']
