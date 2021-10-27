from django.db import models
from django.utils.translation import gettext_lazy as _


class CategoryMap(models.Model):

    # name_in_map = models.CharField(verbose_name=_("name in map"))
    code = models.CharField(verbose_name=_("code"), max_length=255)
    country = models.ForeignKey('geo.Country', verbose_name=_("country"), on_delete=models.CASCADE, related_name='category_map')
    category = models.ForeignKey('budget.Category', verbose_name=_("category"), on_delete=models.CASCADE, related_name='category')

    def __str__(self):
        return f'{self.code} - {self.country} - {self.category}'

    class Meta:
        verbose_name = _("category map")
        # how will be appear in admin
        verbose_name_plural = _("category maps")
        # _("will be translate")
        unique_together = ('code', 'country', 'category')
        # do not repeat
        ordering = ['country', 'category', 'code'] # alter the order list in admin too
        # the default order
