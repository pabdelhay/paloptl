from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import CurrencyField


class Country(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=100)
    slug = models.SlugField()
    flag = models.ImageField(verbose_name=_("flag"), upload_to='countries', null=True, blank=True)
    currency = CurrencyField(verbose_name=_("currency"), choices=settings.CURRENCY_CHOICES)

    class Meta:
        verbose_name = _("country")
        verbose_name_plural = _("countries")
        ordering = ['name']

    def __str__(self):
        return self.name
