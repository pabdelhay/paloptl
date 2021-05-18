import codecs
import csv
import operator
import os
from collections import OrderedDict
from functools import reduce

from dirtyfields import DirtyFieldsMixin
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


class Upload(models.Model, DirtyFieldsMixin):
    budget = models.ForeignKey('budget.Budget', verbose_name=_("budget"), related_name='uploads',
                               on_delete=models.CASCADE)
    file = models.FileField(verbose_name=_("file"), upload_to=get_upload_path,
                            validators=[FileExtensionValidator(allowed_extensions=['csv', 'txt'])])
    report = models.CharField(verbose_name=_("report"), max_length=5, choices=UploadReportChoices.choices)
    status = models.CharField(verbose_name=_("status"), max_length=20, choices=UploadStatusChoices.choices,
                              editable=False)

    errors = ArrayField(models.CharField(max_length=1000), verbose_name=_("errors"), default=list, editable=False)

    uploaded_on = models.DateTimeField(verbose_name=_("uploaded on"), auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("uploaded by"), on_delete=models.PROTECT,
                                    editable=False)

    class Meta:
        ordering = ['uploaded_on']

    def __str__(self):
        return f"{self.budget.country.name} ({self.budget.year}) - #{self.id}"

    def save(self, *args, **kwargs):
        is_new = not self.pk
        if not is_new and 'file' in self.get_dirty_fields():
            self.status = UploadStatusChoices.WAITING_REIMPORT
        super().save(*args, **kwargs)

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
        if comma_count >= 2:
            return ','
        comma_dot_count = partial_header_string.count(b';')
        if comma_dot_count >= 2:
            return ';'

        return default_delimiter

    def validate(self):
        """
        Validate if file is ok to import.
        Validations:
            - Headers
            - Check if each cell's value is according to BudgetUploadSerializer fields
            - Check if there are same category names for different codes
        :return:
        """
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

        class CategoryCheck(object):
            def __init__(self, name, level='category'):
                self.name = name
                self.level = level
                self.codes = set()
                self.lines = list()

            def set_code_and_line(self, code, line):
                self.codes.add(str(code))
                self.lines.append(str(line))

        # {code: CategoryCode}
        categories = dict()
        subcategories = dict()

        if not self.errors:
            # Only check for data fields if header is ok.
            for row in reader:
                line_num = reader.line_num
                data = empty_string_to_none(row)
                serializer = BudgetUploadSerializer(data=data)
                if not serializer.is_valid():
                    for field, errors_list in serializer.errors.items():
                        error_msg = "; ".join(errors_list)
                        self.errors.append(_("<strong>Line {line} ({column})</strong>: {error_msg} Input was: {input}"
                                             .format(line=line_num, column=field, error_msg=error_msg,
                                                     input=row[field])))

                category_code = data.get('category_code', None)
                category_name = data.get('category')
                if category_code:
                    categories.setdefault(category_name, CategoryCheck(name=category_name))
                    categories[category_name].set_code_and_line(category_code, line_num)
                subcategory_code = data.get('subcategory_code', None)
                subcategory_name = data.get('subcategory')
                if subcategory_code:
                    subcategories.setdefault(subcategory_name, CategoryCheck(name=subcategory_name, level='subcategory'))
                    subcategories[subcategory_name].set_code_and_line(subcategory_code, line_num)

        def check_code_errors(categories_dict):
            for cat_name, category_check in categories_dict.items():
                if len(category_check.codes) > 1:
                    lines = ",".join(category_check.lines)
                    codes = ", ".join(category_check.codes)
                    self.errors.append(_("<strong>Lines {lines} ({level}, {level}_code)</strong>: Different codes for "
                                         "{level} <strong>{category}</strong>. Codes: [<strong>{codes}</strong>]"
                                         .format(lines=lines, level=category_check.level, category=cat_name,
                                                 codes=codes)))

        check_code_errors(categories)
        check_code_errors(subcategories)

        return not bool(len(self.errors))

    def do_import(self):
        """
        Make the upload import.
        Same category rows are summed. Final value override existent value on database.
        eg.:
            category  category_code  budget_aggregated
            Security  001            100
            Security  001            50
        Budget aggregated for Security will be 150. This value will override existent value on database.
        :return:
        """
        from api.api_admin import BudgetUploadSerializer
        upload = self

        self.errors = list()  # [string]
        log = list()  # [UploadLog]

        content = self.file.read()
        encoding = self.get_enconding_from_content(content)
        delimiter = self.get_delimiter_from_content(content)
        reader = csv.DictReader(codecs.iterdecode(content.splitlines(), encoding), dialect=csv.excel,
                                delimiter=delimiter)

        # {category_id: {'instance': Category, 'values': {
        #   'budget_investment': float, 'budget_operation': float, 'budget_aggregated': float,
        #   'execution_investment': float, 'execution_operation': float, 'execution_aggregated': float}
        # }
        categories_dict = {}

        def update_category(instance, attr, new_value):
            category_id = instance.id
            categories_dict.setdefault(category_id, {'instance': instance, 'values': {}})
            categories_dict[category_id]['instance'] = instance  # Update instance
            if new_value is not None:
                previous_value_on_same_import = categories_dict[category_id]['values'].get(attr, 0)
                new_value = previous_value_on_same_import + new_value
                categories_dict[category_id]['values'][attr] = new_value

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
                # Get category by name OR code
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
            if row_category_code:
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
                if row_subcategory_code:
                    instance.code = row_subcategory_code

            if self.report == UploadReportChoices.OGE:
                # If is OGE report, save also initial budget values
                update_category(instance=instance, attr='initial_budget_investment',
                                new_value=data['budget_investment'])
                update_category(instance=instance, attr='initial_budget_operation',
                                new_value=data['budget_operation'])
                update_category(instance=instance, attr='initial_budget_aggregated',
                                new_value=data['budget_aggregated'])
            update_category(instance=instance, attr='budget_investment', new_value=data['budget_investment'])
            update_category(instance=instance, attr='budget_operation', new_value=data['budget_operation'])
            update_category(instance=instance, attr='budget_aggregated', new_value=data['budget_aggregated'])
            update_category(instance=instance, attr='execution_investment', new_value=data['execution_investment'])
            update_category(instance=instance, attr='execution_operation', new_value=data['execution_operation'])
            update_category(instance=instance, attr='execution_aggregated', new_value=data['execution_aggregated'])

        # Saving categories after sum of all same category rows.
        for category_id, obj in categories_dict.items():
            category = obj['instance']
            values = obj['values']
            for field, new_value in values.items():
                old_value = getattr(category, field)
                if new_value != old_value:
                    if not (self.report == UploadReportChoices.OGE and field.startswith('initial_')):
                        # Don't log initial values of OGE report.
                        upload_log = UploadLog(upload=upload, log_type=LogTypeChoices.UPDATE,
                                               category=category, field=field, old_value=old_value,
                                               new_value=new_value, updated_by=upload.uploaded_by,
                                               category_name=category.name)
                        log.append(upload_log)
                setattr(category, field, new_value)

                # Remove field from inferred_fields if it was previously inferred.
                was_previously_inferred = category.inferred_fields.get(field, None)
                if was_previously_inferred:
                    category.inferred_fields[field] = False
            category.save()

        try:
            self.save()
            with transaction.atomic():
                UploadLog.objects.bulk_create(log)
        except Exception as exc:
            self.errors.append(str(exc))
            return False

        return self
