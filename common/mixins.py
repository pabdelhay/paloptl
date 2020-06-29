from django.db import models
from django.utils.translation import gettext_lazy as _


class CountryMixin(models.Model):
    country = models.ForeignKey('geo.Country', verbose_name=_("country"), on_delete=models.CASCADE)

    class Meta:
        abstract = True
