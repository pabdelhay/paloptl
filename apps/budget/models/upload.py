import codecs
import csv
import os

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.budget.choices import UploadReportChoices, UploadStatusChoices


def get_upload_path(instance, filename):
    budget = instance.budget
    return os.path.join('reports', budget.country.slug, str(budget.year), filename)


def empty_string_to_none(row):
    for k, v in row.items():
        if v == '':
            row[k] = None
    return row


class Upload(models.Model):
    CSV_DELIMITER = ','

    budget = models.ForeignKey('budget.Budget', verbose_name=_("budget"), on_delete=models.CASCADE)
    file = models.FileField(verbose_name=_("file"), upload_to=get_upload_path,
                            validators=[FileExtensionValidator(allowed_extensions=['csv', 'txt'])])
    report = models.CharField(verbose_name=_("report"), max_length=5, choices=UploadReportChoices.choices)
    status = models.CharField(verbose_name=_("status"), max_length=20, choices=UploadStatusChoices.choices,
                              editable=False)

    errors = ArrayField(models.CharField(max_length=255), verbose_name=_("errors"), null=True, blank=True)
    log = ArrayField(models.CharField(max_length=255), verbose_name=_("log"), null=True, blank=True)

    uploaded_on = models.DateTimeField(verbose_name=_("uploaded on"), auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("uploaded by"), on_delete=models.PROTECT,
                                    editable=False)

    def __str__(self):
        return f"{self.get_report_display()}"

    def validate(self):
        from api.api_admin import BudgetUploadSerializer

        self.errors = list()
        content = self.file.read()
        reader = csv.DictReader(codecs.iterdecode(content.splitlines(), 'utf-8'), dialect=csv.excel,
                                delimiter=self.CSV_DELIMITER)
        header_fields = list(BudgetUploadSerializer._declared_fields.keys())

        if reader.fieldnames != header_fields:
            self.errors.append(_("Header are not standard. They must be exact as {}".format(str(header_fields))))

        return not bool(len(self.errors))

    def do_import(self):
        from api.api_admin import BudgetUploadSerializer

        self.errors = list()
        content = self.file.read()
        reader = csv.DictReader(codecs.iterdecode(content.splitlines(), 'utf-8'), dialect=csv.excel,
                                delimiter=self.CSV_DELIMITER)
        for row in reader:
            serializer = BudgetUploadSerializer(data=empty_string_to_none(row))
            serializer.is_valid()
            data = serializer.data

            if data['report_type'] == 'organic':
                group_class = self.budget.agencies
            elif data['report_type'] == 'functional':
                group_class = self.budget.functions

            try:
                level_0_group = group_class.get(name__iexact=data['group'])
            except ObjectDoesNotExist:
                level_0_group = group_class.create(
                    name=data['group'],
                    parent=None
                )

            if data['subgroup'] is not None:
                # Budget for a subgroup
                try:
                    level_1_group = group_class.get(name=data['subgroup'])
                except ObjectDoesNotExist:
                    level_1_group = group_class.create(
                        name=data['subgroup'],
                        parent=level_0_group,
                        budget_investment=data['budget_investment'],
                        budget_operation=data['budget_operation'],
                        budget_aggregated=data['budget_aggregated'],
                        execution_investment=data['execution_investment'],
                        execution_operation=data['execution_operation'],
                        execution_aggregated=data['execution_aggregated']
                    )
            else:
                # Budget for the root group.
                level_0_group.budget_investment = data['budget_investment'],
                level_0_group.budget_operation = data['budget_operation'],
                level_0_group.budget_aggregated = data['budget_aggregated'],
                level_0_group.execution_investment = data['execution_investment'],
                level_0_group.execution_operation = data['execution_operation'],
                level_0_group.execution_aggregated = data['execution_aggregated']
                level_0_group.save()

        # TODO: Update aggregated budget and execution for group
        # TODO: Write log.
