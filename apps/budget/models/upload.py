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

    budget = models.ForeignKey('budget.Budget', verbose_name=_("budget"), related_name='uploads',
                               on_delete=models.CASCADE)
    file = models.FileField(verbose_name=_("file"), upload_to=get_upload_path,
                            validators=[FileExtensionValidator(allowed_extensions=['csv', 'txt'])])
    report = models.CharField(verbose_name=_("report"), max_length=5, choices=UploadReportChoices.choices)
    status = models.CharField(verbose_name=_("status"), max_length=20, choices=UploadStatusChoices.choices,
                              editable=False)

    errors = ArrayField(models.CharField(max_length=1000), verbose_name=_("errors"), default=list, editable=False)
    log = ArrayField(models.CharField(max_length=1000), verbose_name=_("log"), default=list, editable=False)

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
            self.errors.append(_("<strong>Line {line}:</strong> Header is not in standard. "
                                 "It must be exact as <i>{header_fields}</i>"
                                 .format(line=reader.line_num, header_fields=str(header_fields))))
        for row in reader:
            serializer = BudgetUploadSerializer(data=empty_string_to_none(row))
            if not serializer.is_valid():
                for field, errors_list in serializer.errors.items():
                    error_msg = "; ".join(errors_list)
                    self.errors.append(_("<strong>Line {line} ({column})</strong>: {error_msg}"
                                         .format(line=reader.line_num, column=field, error_msg=error_msg)))

        return not bool(len(self.errors))

    def do_import(self):
        from api.api_admin import BudgetUploadSerializer

        self.errors = list()
        self.log = list()
        content = self.file.read()
        reader = csv.DictReader(codecs.iterdecode(content.splitlines(), 'utf-8'), dialect=csv.excel,
                                delimiter=self.CSV_DELIMITER)

        def update_category(instance, attr, new_value):
            old_value = getattr(instance, attr)
            field_name = instance.__class__._meta.get_field(attr).verbose_name
            level = 1 if instance.parent else 0
            if old_value != new_value:
                setattr(instance, attr, new_value)
                self.log.append(_("Updated {taxonomy} <strong>{name}</strong> <i>{field_name}</i> from {old_value} "
                                  "to {new_value}".format(taxonomy=instance.get_taxonomy(level=level),
                                                          name=instance.get_hierarchy_name(), field_name=field_name,
                                                          old_value=old_value or _("(empty)"), new_value=new_value)))

        for row in reader:
            serializer = BudgetUploadSerializer(data=empty_string_to_none(row))
            serializer.is_valid()
            data = serializer.data

            row_report_type = data['report_type']
            row_category = data['category']
            row_subcategory = data['subcategory']

            # Check if report is organic or functional.
            if row_report_type == 'organic':
                category_set = self.budget.agencies
                category_model = self.budget.agencies.model
            elif row_report_type == 'functional':
                category_set = self.budget.functions
                category_model = self.budget.functions.model

            try:
                category = category_set.get(name__iexact=row_category, parent__isnull=True)
            except ObjectDoesNotExist:
                category = category_set.create(name=row_category)
                self.log.append(_("Created {taxonomy} <strong>{name}</strong>"
                                  .format(taxonomy=category_model.get_taxonomy(level=0), name=row_category)))

            instance = category
            if row_subcategory is not None:
                # Budget for a subgroup
                try:
                    subcategory = category_set.get(name=row_subcategory, parent=category)
                except ObjectDoesNotExist:
                    subcategory = category_model(name=row_subcategory, parent=category, budget=self.budget)
                    self.log.append(_("Created {taxonomy} <strong>{name}</strong>"
                                      .format(taxonomy=category_model.get_taxonomy(level=1),
                                              name=subcategory.get_hierarchy_name())))
                instance = subcategory

            update_category(instance=instance, attr='budget_investment', new_value=data['budget_investment'])
            update_category(instance=instance, attr='budget_operation', new_value=data['budget_operation'])
            update_category(instance=instance, attr='budget_aggregated', new_value=data['budget_aggregated'])
            update_category(instance=instance, attr='execution_investment', new_value=data['execution_investment'])
            update_category(instance=instance, attr='execution_operation', new_value=data['execution_operation'])
            update_category(instance=instance, attr='execution_aggregated', new_value=data['execution_aggregated'])
            if self.report == UploadReportChoices.OGE:
                # If is OGE report, save also initial budget values
                update_category(instance=instance, attr='initial_budget_investment',
                                new_value=data['budget_investment'])
                update_category(instance=instance, attr='initial_budget_operation',
                                new_value=data['budget_operation'])
                update_category(instance=instance, attr='initial_budget_aggregated',
                                new_value=data['budget_aggregated'])
            instance.save()

        try:
            self.save()
        except Exception as exc:
            self.errors.append(str(exc))
            return False

        return self
