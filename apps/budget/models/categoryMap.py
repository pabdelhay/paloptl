from django.db import models
from django.utils.translation import gettext_lazy as _

from common.mixins import CountryMixin


class CategoryMap(CountryMixin, models.Model):
    """
    The Category mapping comparable per country
    """

    code = models.CharField(verbose_name=_("code"), max_length=30)

    country = models.ForeignKey('geo.Country', verbose_name=_("country"), on_delete=models.CASCADE,
                                related_name='category_map')

    category = models.ForeignKey('budget.Category', verbose_name=_("category"), on_delete=models.CASCADE,
                                 related_name='category_map')

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _("Category Mappping")
        verbose_name_plural = _("Categories Mappping")
        unique_together = ('code', 'country', 'category')
        ordering = ['category', 'country']
