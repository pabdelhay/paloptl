from django.conf import settings
from django.db import models
from djmoney.models.fields import CurrencyField

from common.mixins import CountryMixin
from django.utils.translation import gettext_lazy as _


class Budget(CountryMixin, models.Model):
    """
    A (year, country) aggregation of budget data.
    """
    year = models.IntegerField(verbose_name=_("year"))
    currency = CurrencyField(choices=settings.CURRENCY_CHOICES, editable=False,
                             help_text=_("All values from budget presented in this currency"))

    class Meta:
        verbose_name = _("budget")
        verbose_name_plural = _("budgets")
        ordering = ['country', '-year']

    def __str__(self):
        return f"{self.country.name} - {self.year}"

    def save(self, *args, **kwargs):
        is_new = not self.pk
        if is_new:
            self.currency = self.country.currency
        super().save(*args, **kwargs)
