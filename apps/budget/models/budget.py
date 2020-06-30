from django.db import models

from common.mixins import CountryMixin
from django.utils.translation import gettext_lazy as _


class Budget(CountryMixin, models.Model):
    """
    A (year, country) aggregation of budget data.
    """
    year = models.IntegerField(verbose_name=_("year"))

    class Meta:
        verbose_name = _("budget")
        verbose_name_plural = _("budgets")

    def __str__(self):
        return f"{self.country.name} - {self.year}"
