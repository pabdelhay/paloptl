import codecs
import csv
import operator
import os
from functools import reduce

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.budget.choices import UploadReportChoices, UploadStatusChoices, LogTypeChoices
from apps.budget.models.upload_log import UploadLog


def get_upload_path(instance, filename):
    budget = instance.budget
    return os.path.join('reports', budget.country.slug, str(budget.year), filename)


def empty_string_to_none(row):
    for k, v in row.items():
        row[k] = row[k].strip()
        if v == '':
            row[k] = None
    return row


class Upload(models.Model):
    budget = models.ForeignKey('budget.Budget', verbose_name=_("budget"), related_name='uploads',
                               on_delete=models.CASCADE)
    file = models.FileField(verbose_name=_("file"), upload_to=get_upload_path,
                            validators=[FileExtensionValidator(allowed_extensions=['csv', 'txt'])])
    report = models.CharField(verbose_name=_("report"), max_length=5, choices=UploadReportChoices.choices)
    status = models.CharField(verbose_name=_("status"), max_length=20, choices=UploadStatusChoices.choices,
                              editable=False)

    errors = ArrayField(models.CharField(max_length=1000), verbose_name=_("errors"), default=list, editable=False)
    # TODO: Remove after migrate to UploadLog
    log = ArrayField(models.CharField(max_length=1000), verbose_name=_("log"), default=list, editable=False)

    uploaded_on = models.DateTimeField(verbose_name=_("uploaded on"), auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("uploaded by"), on_delete=models.PROTECT,
                                    editable=False)

    def __str__(self):
        return f"{self.budget.country.name} ({self.budget.year}) - #{self.id}"

    @classmethod
    def get_enconding_from_content(cls, content):
        if content[:1] == b'\xef':
            return 'utf-8-sig'
        return 'utf-8'

    @classmethod
    def get_delimiter_from_content(cls, content):
        """
        Guess CSV delimiter from a partial of header string.
        :param content: byte
        :return: string (';' or ',')
        """
        default_delimiter = ','

        partial_header_string = content[:50]
        comma_count = partial_header_string.count(b',')
        if comma_count > 2:
            return ','
        comma_dot_count = partial_header_string.count(b';')
        if comma_dot_count > 2:
            return ';'

        return default_delimiter

    def validate(self):
        from api.api_admin import BudgetUploadSerializer

        self.errors = list()
        content = self.file.read()
        encoding = self.get_enconding_from_content(content)
        delimiter = self.get_delimiter_from_content(content)
        reader = csv.DictReader(codecs.iterdecode(content.splitlines(), encoding), dialect=csv.excel,
                                delimiter=delimiter)

        # # Validate headers
        header_fields = list(BudgetUploadSerializer._declared_fields.keys())

        for field in reader.fieldnames:
            if field not in header_fields:
                if field.strip() in header_fields:
                    self.errors.append(_("<strong>Line {line}:</strong> <b>'{field}'</b> is not a valid header. "
                                         "Did you mean: <b>'{field_correct}'</b>? "
                                         "<small>Remove any white spaces before and after the field.</small>"
                                         .format(line=reader.line_num, field=field, field_correct=field.strip())))
                else:
                    self.errors.append(_("<strong>Line {line}:</strong> <b>'{field}'</b> is not a valid header. "
                                         "It must be exact one of: <i>{header_fields}</i>"
                                         .format(line=reader.line_num, field=field, header_fields=str(header_fields))))

        if not self.errors:
            # Only check for data fields if header is ok.
            for row in reader:
                serializer = BudgetUploadSerializer(data=empty_string_to_none(row))
                if not serializer.is_valid():
                    for field, errors_list in serializer.errors.items():
                        error_msg = "; ".join(errors_list)
                        self.errors.append(_("<strong>Line {line} ({column})</strong>: {error_msg} Input was: {input}"
                                             .format(line=reader.line_num, column=field, error_msg=error_msg,
                                                     input=row[field])))

        return not bool(len(self.errors))

    def do_import(self):
        from api.api_admin import BudgetUploadSerializer
        upload = self

        self.errors = list()  # [string]
        log = list()  # [UploadLog]

        content = self.file.read()
        encoding = self.get_enconding_from_content(content)
        delimiter = self.get_delimiter_from_content(content)
        reader = csv.DictReader(codecs.iterdecode(content.splitlines(), encoding), dialect=csv.excel,
                                delimiter=delimiter)

        def update_category(instance, attr, new_value, add_log=True):
            old_value = getattr(instance, attr)

            if new_value is not None:
                # Remove field from inferred_fields if it was previously inferred.
                was_previously_inferred = instance.inferred_fields.get(attr, None)
                if was_previously_inferred:
                    instance.inferred_fields[attr] = False

                if old_value != new_value:
                    # Set new value and add to log.
                    setattr(instance, attr, new_value)

                    if add_log:
                        upload_log = UploadLog(upload=upload, log_type=LogTypeChoices.UPDATE,
                                               category=instance, field=attr, old_value=old_value,
                                               new_value=new_value, updated_by=upload.uploaded_by,
                                               category_name=instance.name)
                        log.append(upload_log)

        for row in reader:
            serializer = BudgetUploadSerializer(data=empty_string_to_none(row))
            serializer.is_valid()
            data = serializer.data

            row_report_type = data['report_type']
            row_category = data['category']
            row_subcategory = data['subcategory']
            row_category_code = data['category_code']
            row_subcategory_code = data['subcategory_code']

            # Check if report is organic or functional.
            if row_report_type == 'organic':
                category_set = self.budget.agencies
                category_model = self.budget.agencies.model
            elif row_report_type == 'functional':
                category_set = self.budget.functions
                category_model = self.budget.functions.model

            try:
                filters = [Q(name__iexact=row_category)]
                if row_category_code:
                    filters.append(Q(code=row_category_code))
                category = category_set.filter(parent__isnull=True).get(reduce(operator.or_, filters))
            except ObjectDoesNotExist:
                category = category_set.create(name=row_category, code=row_category_code)
                upload_log = UploadLog(upload=upload, log_type=LogTypeChoices.NEW_CATEGORY, category=category,
                                       updated_by=upload.uploaded_by, category_name=category.name)
                log.append(upload_log)

            instance = category
            instance.code = row_category_code
            if row_subcategory is not None:
                # Budget for a subgroup
                try:
                    filters = [Q(name__iexact=row_subcategory)]
                    if row_subcategory_code:
                        filters.append(Q(code=row_subcategory_code))
                    subcategory = category_set.filter(parent=category).get(reduce(operator.or_, filters))
                except ObjectDoesNotExist:
                    subcategory = category_set.create(name=row_subcategory, parent=category, budget=self.budget,
                                                      code=row_subcategory_code)
                    upload_log = UploadLog(upload=upload, log_type=LogTypeChoices.NEW_CATEGORY, category=subcategory,
                                           updated_by=upload.uploaded_by, category_name=subcategory.name)
                    log.append(upload_log)

                instance = subcategory
                instance.code = row_subcategory_code

            if self.report == UploadReportChoices.OGE:
                # If is OGE report, save also initial budget values
                update_category(instance=instance, attr='initial_budget_investment',
                                new_value=data['budget_investment'])
                update_category(instance=instance, attr='initial_budget_operation',
                                new_value=data['budget_operation'])
                update_category(instance=instance, attr='initial_budget_aggregated',
                                new_value=data['budget_aggregated'])
                update_category(instance=instance, attr='budget_investment', new_value=data['budget_investment'],
                                add_log=False)
                update_category(instance=instance, attr='budget_operation', new_value=data['budget_operation'],
                                add_log=False)
                update_category(instance=instance, attr='budget_aggregated', new_value=data['budget_aggregated'],
                                add_log=False)
            else:
                update_category(instance=instance, attr='budget_investment', new_value=data['budget_investment'])
                update_category(instance=instance, attr='budget_operation', new_value=data['budget_operation'])
                update_category(instance=instance, attr='budget_aggregated', new_value=data['budget_aggregated'])
            update_category(instance=instance, attr='execution_investment', new_value=data['execution_investment'])
            update_category(instance=instance, attr='execution_operation', new_value=data['execution_operation'])
            update_category(instance=instance, attr='execution_aggregated', new_value=data['execution_aggregated'])

            instance.save()

        try:
            self.save()
            with transaction.atomic():
                UploadLog.objects.bulk_create(log)
        except Exception as exc:
            self.errors.append(str(exc))
            return False

        return self
