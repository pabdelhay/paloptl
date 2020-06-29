import codecs
import csv
import os

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.budget.choices import UploadReportChoices, UploadStatusChoices


def get_upload_path(instance, filename):
    budget = instance.budget
    return os.path.join('reports', budget.country.slug, str(budget.year), filename)


class Upload(models.Model):
    CSV_DELIMITER = ','

    budget = models.ForeignKey('budget.Budget', verbose_name=_("budget"), on_delete=models.CASCADE)
    file = models.FileField(verbose_name=_("file"), upload_to=get_upload_path,
                            validators=[FileExtensionValidator(allowed_extensions=['csv', 'txt'])])
    report = models.CharField(verbose_name=_("report"), max_length=5, choices=UploadReportChoices.choices)
    status = models.CharField(verbose_name=_("status"), max_length=20, choices=UploadStatusChoices.choices,
                              editable=False)

    uploaded_on = models.DateTimeField(verbose_name=_("uploaded on"), auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("uploaded by"), on_delete=models.PROTECT,
                                    editable=False)

    def __str__(self):
        return f"{self.get_report_display()}"

    def validate(self):
        content = self.file.read()
        reader = csv.DictReader(codecs.iterdecode(content.splitlines(), 'utf-8'), dialect=csv.excel,
                                delimiter=self.CSV_DELIMITER)
        return True
