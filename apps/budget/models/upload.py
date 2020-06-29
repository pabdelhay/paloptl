from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.budget.choices import UploadReportChoices


class Upload(models.Model):
    budget = models.ForeignKey('budget.Budget', verbose_name=_("budget"), on_delete=models.CASCADE)
    file = models.FileField(verbose_name=_("file"), upload_to='uploads')
    report = models.CharField(verbose_name=_("report"), max_length=5, choices=UploadReportChoices.choices)

    uploaded_on = models.DateTimeField(verbose_name=_("uploaded on"), auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("uploaded by"), on_delete=models.PROTECT,
                                    editable=False)

    def __str__(self):
        return f"{self.get_report_display()}"
