from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.mixins import CountryMixin


class TransparencyIndex(CountryMixin, models.Model):
    """
    The transparency Index aggregated per (country, year)
    """
    country = models.ForeignKey('geo.Country', verbose_name=_("country"), on_delete=models.CASCADE,
                                related_name='index')
    year = models.IntegerField(verbose_name=_("year"))

    score_open_data = models.SmallIntegerField(verbose_name=_("score - open data"), help_text="0 - 100",
                                               null=True, blank=True, validators=[MinValueValidator(0),
                                                                                  MaxValueValidator(100)])
    score_reports = models.SmallIntegerField(verbose_name=_("score - reports"), help_text="0 - 100",
                                             null=True, blank=True, validators=[MinValueValidator(0),
                                                                                MaxValueValidator(100)])
    score_data_quality = models.SmallIntegerField(verbose_name=_("score - data quality"), help_text="0 - 200",
                                                  null=True, blank=True, validators=[MinValueValidator(0),
                                                                                     MaxValueValidator(200)])
    transparency_index = models.SmallIntegerField(verbose_name=_("transparency index"), help_text="0 - 100",
                                                  null=True, blank=True, validators=[MinValueValidator(0),
                                                                                     MaxValueValidator(100)])

    def __str__(self):
        return f'{self.country} - {self.year}'

    class Meta:
        verbose_name = _("transparency index")
        verbose_name_plural = _("transparency index")
        unique_together = ('country', 'year')
        ordering = ['country', '-year']
