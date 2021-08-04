import codecs
import csv
import operator
import os
from functools import reduce

from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.budget.choices import UploadReportChoices, UploadStatusChoices, LogTypeChoices, UploadCategoryChoices
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
    category = models.CharField(verbose_name=_("category"), max_length=10,
                                choices=UploadCategoryChoices.choices, default=UploadCategoryChoices.EXPENSE)
    report = models.CharField(verbose_name=_("report"), max_length=5, choices=UploadReportChoices.choices)
    status = models.CharField(verbose_name=_("status"), max_length=20, choices=UploadStatusChoices.choices,
                              editable=False)

    errors = ArrayField(models.CharField(max_length=1000), verbose_name=_("errors"), default=list, editable=False)

    uploaded_on = models.DateTimeField(verbose_name=_("uploaded on"), auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("uploaded by"), on_delete=models.PROTECT,
                                    editable=False)
    updated_on = models.DateTimeField(verbose_name=_("updated on"), auto_now_add=True)

    class Meta:
        ordering = ['uploaded_on']

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
        from api.api_admin import ExpenseUploadSerializer, RevenueUploadSerializer

        self.errors = list()
        content = self.file.read()
        encoding = self.get_enconding_from_content(content)
        delimiter = self.get_delimiter_from_content(content)
        reader = csv.DictReader(codecs.iterdecode(content.splitlines(), encoding), dialect=csv.excel,
                                delimiter=delimiter)

        if self.category == UploadCategoryChoices.EXPENSE:
            serializer_class = ExpenseUploadSerializer
        elif self.category == UploadCategoryChoices.REVENUE:
            serializer_class = RevenueUploadSerializer

        # Validate headers
        header_fields = list(serializer_class._declared_fields.keys())
        mandatory_fields = ['group', 'category']

        for field in mandatory_fields:
            if field not in reader.fieldnames:
                if field == 'group':
                    if 'report_type' in reader.fieldnames:
                        # report_type is the old field name for group. We still accept it.
                        continue
                self.errors.append(_("<strong>Line {line}:</strong> Missing <b>'{field}'</b> column.")
                                   .format(line=reader.line_num, field=field))

        for field in reader.fieldnames:
            if field not in header_fields:
                if field.strip() in header_fields:
                    self.errors.append(_("<strong>Line {line}:</strong> <b>'{field}'</b> is not a valid header. "
                                         "Did you mean: <b>'{field_correct}'</b>? "
                                         "<small>Remove any white spaces before and after the field.</small>"
                                         .format(line=reader.line_num, field=field, field_correct=field.strip())))
                else:
                    self.errors.append(_("<strong>Line {line}:</strong> <b>'{field}'</b> is not a valid header. "
                                         "It must be one of: <i>{header_fields}</i>"
                                         .format(line=reader.line_num, field=field, header_fields=str(header_fields))))

        class CategoryCheck(object):
            def __init__(self, name=None, code=None, level='category'):
                self.name = name
                self.code = code
                self.level = level
                self.codes = set()
                self.names = set()
                self.lines = list()

            def set_code_and_line(self, code, line):
                self.codes.add(str(code))
                self.lines.append(str(line))

            def set_name_and_line(self, name, line):
                self.names.add(name)
                self.lines.append(str(line))

        # {name: CategoryCheck}
        categories_by_name = dict()
        # {code: CategoryCheck}
        categories_by_code = dict()

        if not self.errors:
            # Only check for data fields if header is ok.
            for row in reader:
                line_num = reader.line_num
                data = empty_string_to_none(row)
                serializer = serializer_class(data=data)
                if not serializer.is_valid():
                    for field, errors_list in serializer.errors.items():
                        input = row.get(field, "''")
                        if len(errors_list) == 1:
                            err = errors_list[0]
                            error_msg = str(err)
                            if err.code == 'invalid_choice':
                                available_choices = serializer.fields.fields[field].choices.keys()
                                available_choices_str = ", ".join(available_choices)
                                error_msg += f" Available choices are: <strong>{available_choices_str}</strong> for " \
                                             f"{self.get_category_display().lower()}s."
                            self.errors.append(
                                _("<strong>Line {line} ({column})</strong>: {error_msg} Input was: {input}"
                                  .format(line=line_num, column=field, error_msg=error_msg, input=input)))
                        else:
                            error_msg = "; ".join(errors_list)
                            self.errors \
                                .append(_("<strong>Line {line} ({column})</strong>: {error_msg} Input was: {input}"
                                          .format(line=line_num, column=field, error_msg=error_msg, input=input)))

                category_code = data.get('category_code', None)
                category_name = data.get('category')
                if category_code:
                    categories_by_name.setdefault(category_name, CategoryCheck(name=category_name))
                    categories_by_name[category_name].set_code_and_line(category_code, line_num)
                    categories_by_code.setdefault(category_code, CategoryCheck(code=category_code))
                    categories_by_code[category_code].set_name_and_line(category_name, line_num)
                subcategory_code = data.get('subcategory_code', None)
                subcategory_name = data.get('subcategory')
                if subcategory_code:
                    subcategory_name_key = f"{category_name} - {subcategory_name}"
                    subcategory_code_key = f"{category_name} - {subcategory_code}"
                    categories_by_name.setdefault(subcategory_name_key,
                                                  CategoryCheck(name=subcategory_name, level='subcategory'))
                    categories_by_name[subcategory_name_key].set_code_and_line(subcategory_code, line_num)
                    categories_by_code.setdefault(subcategory_code_key,
                                                  CategoryCheck(code=subcategory_code, level='subcategory'))
                    categories_by_code[subcategory_code_key].set_name_and_line(subcategory_name, line_num)

        def check_code_errors(categories_dict, dict_by='name'):
            attr_check = 'codes' if dict_by == 'name' else 'names'
            for cat_name, category_check in categories_dict.items():
                if len(getattr(category_check, attr_check)) > 1:
                    lines = ",".join(category_check.lines)

                    duplicated_objs = ", ".join(category_check.codes)
                    category_label = category_check.name
                    if dict_by == 'code':
                        duplicated_objs = ", ".join(category_check.names)
                        category_label = category_check.code

                    self.errors.append(
                        _("<strong>Lines {lines} ({level}, {level}_code)</strong>: Different {attr_check} "
                          "for {level} <strong>{category}</strong>. {attr_check}: [<strong>{duplicated_objs}</strong>]"
                          .format(lines=lines, level=category_check.level, attr_check=attr_check,
                                  category=category_label, duplicated_objs=duplicated_objs))
                        )

        check_code_errors(categories_by_name, dict_by='name')
        check_code_errors(categories_by_code, dict_by='code')

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
        from api.api_admin import ExpenseUploadSerializer, RevenueUploadSerializer
        upload = self

        self.errors = list()  # [string]
        log = list()  # [UploadLog]

        content = self.file.read()
        encoding = self.get_enconding_from_content(content)
        delimiter = self.get_delimiter_from_content(content)
        reader = csv.DictReader(codecs.iterdecode(content.splitlines(), encoding), dialect=csv.excel,
                                delimiter=delimiter)

        if self.category == UploadCategoryChoices.EXPENSE:
            serializer_class = ExpenseUploadSerializer
        elif self.category == UploadCategoryChoices.REVENUE:
            serializer_class = RevenueUploadSerializer

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
            serializer = serializer_class(data=empty_string_to_none(row))
            serializer.is_valid()
            data = serializer.data

            # report_type is deprecated. Here for backward compatibility
            row_group = data.get('group') or data.get('report_type')
            row_category = data['category']
            row_subcategory = data['subcategory']
            row_category_code = data['category_code']
            row_subcategory_code = data['subcategory_code']

            # Check if report is organic or functional.
            if self.category == UploadCategoryChoices.EXPENSE:
                category_set = self.budget.expenses
            elif self.category == UploadCategoryChoices.REVENUE:
                category_set = self.budget.revenues

            try:
                # Get category by name OR code
                filters = [Q(name__iexact=row_category)]
                if row_category_code:
                    filters.append(Q(code=row_category_code))
                category = category_set.filter(group=row_group, parent__isnull=True).get(reduce(operator.or_, filters))
            except ObjectDoesNotExist:
                category = category_set.create(group=row_group, name=row_category, code=row_category_code)
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
                    subcategory = category_set.filter(group=row_group, parent=category)\
                        .get(reduce(operator.or_, filters))
                except ObjectDoesNotExist:
                    subcategory = category_set.create(group=row_group, name=row_subcategory, parent=category,
                                                      budget=self.budget, code=row_subcategory_code)
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
