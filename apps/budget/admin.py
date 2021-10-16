from admin_honeypot.models import LoginAttempt
from django.contrib import admin, messages
from django.contrib.admin import TabularInline
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_admin_inline_paginator.admin import TabularInlinePaginated
from tabulate import tabulate

from apps.budget.choices import UploadStatusChoices, ExpenseGroupChoices, RevenueGroupChoices, UploadCategoryChoices
from apps.budget.models import Upload, Budget, UploadLog, BudgetSummary, Expense, Revenue
from apps.budget.models.transparency_index import TransparencyIndex
from apps.budget.tasks import import_file, reimport_budget_uploads
from common.admin import CountryPermissionMixin
from common.methods import raw_money_display

admin.site.unregister(LoginAttempt)


class UploadInline(admin.TabularInline):
    model = Upload
    extra = 1
    fields = ('file', 'category', 'report', 'status', 'get_log', 'uploaded_by', 'updated_on')
    readonly_fields = ('status', 'uploaded_by', 'updated_on', 'get_log')

    @mark_safe
    def get_log(self, obj):
        if not obj.id:
            return "-"

        html = "-"
        if obj.status in UploadStatusChoices.get_error_status():
            link_text = _("Errors") + f" ({len(obj.errors)})"
            errors = "<br>".join(obj.errors)
            html = f'<div class="upload-log" id="upload-dialog-{obj.id}">{errors}</div>' \
                   f'<a href="#" class="log-link" data-upload_id="{obj.id}">{link_text}</a>' \

        elif obj.status in UploadStatusChoices.get_success_status():
            log_count = obj.logs.count()
            log_link = reverse(f'admin:budget_uploadlog_changelist') + f'?upload_id={obj.id}&_popup=1'
            html = f'<a href="{log_link}" target="popup" ' \
                   f'onclick=\'window.open("{log_link}","popup","width=1200,height=800"); return false;\'>' \
                   f'Log ({log_count})</a>'

        return f'<div class="upload-log-wrapper">' \
               f'   <input type="hidden" name="status-{obj.id}" class="status-input" value="{obj.status}">' \
               f'' + html + \
               f'</div>'
    get_log.short_description = "log"


class BudgetSummaryInline(TabularInline):
    model = BudgetSummary
    fields = ('expense_functional_budget', 'expense_functional_execution',
              'expense_organic_budget', 'expense_organic_execution',
              'revenue_nature_budget', 'revenue_nature_execution',
              'revenue_source_budget', 'revenue_source_execution')
    readonly_fields = ('expense_functional_budget', 'expense_functional_execution',
                       'expense_organic_budget', 'expense_organic_execution',
                       'revenue_nature_budget', 'revenue_nature_execution',
                       'revenue_source_budget', 'revenue_source_execution')

    def has_delete_permission(self, request, obj=None):
        return False


class BudgetAccountInline(TabularInlinePaginated):
    extra = 0
    per_page = 50
    can_delete = True
    readonly_fields = ('code', 'get_group_taxonomy', 'get_subgroup_taxonomy', 'last_update',
                       'get_budget_investment', 'get_budget_operation', 'get_budget_aggregated',
                       'get_execution_investment', 'get_execution_operation', 'get_execution_aggregated')
    fields = ('code', 'get_group_taxonomy', 'get_subgroup_taxonomy', 'get_budget_investment', 'get_budget_operation',
              'get_budget_aggregated', 'get_execution_investment', 'get_execution_operation',
              'get_execution_aggregated', 'last_update')
    list_select_related = ('parent',)

    classes = ['collapse']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return [
                'code', 'get_group_taxonomy', 'get_subgroup_taxonomy', 'budget_investment', 'budget_operation',
                'budget_aggregated', 'execution_investment', 'execution_operation', 'execution_aggregated',
                'last_update'
            ]
        return self.fields

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return request.user.is_superuser

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(group=self.group).select_related('parent')

    @staticmethod
    def _get_budget_field(obj, field):
        current_value = getattr(obj, field)
        inferred_value = obj.inferred_values.get(field, None)
        if not current_value and not inferred_value:
            return "-"

        final_value = current_value
        class_name = ''
        title = ''
        if obj.inferred_fields.get(field, None):
            final_value = inferred_value
            class_name = 'inferred-value'
            title = _("Value inferred from descendants or siblings.")
        if inferred_value and current_value != inferred_value:
            class_name = 'inferred-different-from-current'
            title = _("Explicit given value differs from inferred value: {inferred}"
                      .format(inferred=raw_money_display(inferred_value)))

        html = f'<span class="{class_name}" title="{title}">{raw_money_display(final_value)}</span>'

        # Value different from initial.
        initial_value = getattr(obj, f"initial_{field}", None)
        if initial_value and initial_value != final_value:
            value_updated_text = _("Showing updated value. Initial value was")
            raw_initial_value = raw_money_display(initial_value)
            html = f'<span class="ui-icon ui-icon-arrowrefresh-1-e trigger-initial-value" ' \
                   f'title="{value_updated_text}: {raw_initial_value}"></span> ' + html

        return html

    @mark_safe
    def get_budget_investment(self, obj):
        return self._get_budget_field(obj, 'budget_investment')

    @mark_safe
    def get_budget_operation(self, obj):
        return self._get_budget_field(obj, 'budget_operation')

    @mark_safe
    def get_budget_aggregated(self, obj):
        return self._get_budget_field(obj, 'budget_aggregated')

    @mark_safe
    def get_execution_investment(self, obj):
        return self._get_budget_field(obj, 'execution_investment')

    @mark_safe
    def get_execution_operation(self, obj):
        return self._get_budget_field(obj, 'execution_operation')

    @mark_safe
    def get_execution_aggregated(self, obj):
        return self._get_budget_field(obj, 'execution_aggregated')

    get_budget_investment.short_description = _("investment budget")
    get_budget_operation.short_description = _("operation budget")
    get_budget_aggregated.short_description = _("total budget")
    get_execution_investment.short_description = _("investment execution")
    get_execution_operation.short_description = _("operation execution")
    get_execution_aggregated.short_description = _("total execution")


class ExpenseFunctionInline(BudgetAccountInline):
    model = Expense
    group = ExpenseGroupChoices.FUNCTIONAL
    verbose_name_plural = _("Expenses by function")

    def get_group_taxonomy(self, obj):
        return obj.parent.name if obj.parent else obj.name
    get_group_taxonomy.short_description = model.get_taxonomy(group=group, level=0)

    def get_subgroup_taxonomy(self, obj):
        return obj.name if obj.parent else ""
    get_subgroup_taxonomy.short_description = model.get_taxonomy(group=group, level=1)


class ExpenseAgencyInline(BudgetAccountInline):
    model = Expense
    group = ExpenseGroupChoices.ORGANIC
    verbose_name_plural = _("Expenses by agency")
    list_select_related = ('parent', )

    def get_group_taxonomy(self, obj):
        return obj.parent.name if obj.parent else obj.name
    get_group_taxonomy.short_description = model.get_taxonomy(group=group, level=0)

    def get_subgroup_taxonomy(self, obj):
        return obj.name if obj.parent else ""
    get_subgroup_taxonomy.short_description = model.get_taxonomy(group=group, level=1)


class RevenueNatureInline(BudgetAccountInline):
    model = Revenue
    group = RevenueGroupChoices.NATURE
    verbose_name_plural = _("Revenues by nature")

    def get_group_taxonomy(self, obj):
        return obj.parent.name if obj.parent else obj.name
    get_group_taxonomy.short_description = model.get_taxonomy(group=group, level=0)

    def get_subgroup_taxonomy(self, obj):
        return obj.name if obj.parent else ""
    get_subgroup_taxonomy.short_description = model.get_taxonomy(group=group, level=1)


class RevenueSourceInline(BudgetAccountInline):
    model = Revenue
    group = RevenueGroupChoices.SOURCE
    verbose_name_plural = _("Revenues by source")

    def get_group_taxonomy(self, obj):
        return obj.parent.name if obj.parent else obj.name
    get_group_taxonomy.short_description = model.get_taxonomy(group=group, level=0)

    def get_subgroup_taxonomy(self, obj):
        return obj.name if obj.parent else ""
    get_subgroup_taxonomy.short_description = model.get_taxonomy(group=group, level=1)


@admin.register(Budget)
class BudgetAdmin(CountryPermissionMixin, admin.ModelAdmin):
    fieldsets = (
        ("Base info", {
            'fields': ('country', 'year', 'is_active', 'currency', 'output_file')
        }),
    )
    inlines = (UploadInline, BudgetSummaryInline,
               ExpenseFunctionInline, ExpenseAgencyInline, RevenueNatureInline, RevenueSourceInline)
    list_display = ('country', 'year', 'is_active', 'uploads', 'uploads_with_error')
    list_filter = ('year', )
    readonly_fields = ('currency', 'output_file')
    actions = ['reimport_uploads', 'remove_uploads_with_error']

    def save_formset(self, request, form, formset, change):
        if formset.model != Upload:
            return super().save_formset(request, form, formset, change)

        instances = formset.save(commit=False)
        uploads_count = len(instances)
        i = 1
        for instance in instances:
            is_new = not instance.pk
            is_last_upload = True if i == uploads_count else False
            force_reimport = False
            if is_new:
                instance.uploaded_by = request.user
                instance.status = UploadStatusChoices.VALIDATING
            elif 'file' in instance.get_dirty_fields():
                instance.uploaded_by = request.user
                instance.updated_on = timezone.now()
                if is_last_upload and instance.status in UploadStatusChoices.get_error_status():
                    # Reimport last upload with error automatically.
                    force_reimport = True
                    instance.status = UploadStatusChoices.VALIDATING
                else:
                    instance.status = UploadStatusChoices.WAITING_REIMPORT
            instance.save()
            if is_new or force_reimport:
                request.session['upload_in_progress'] = instance.id
                async_task = import_file.apply_async(kwargs={'upload_id': instance.id}, countdown=5)
                if async_task.status == 'SUCCESS':
                    # For easter execution of import_file (synchronous on dev mode)
                    instance.refresh_from_db()
                    instance.save()
                elif async_task.status == 'FAILURE':
                    # TODO: Resolve unmapped errors.
                    pass
            i += 1
        formset.save(commit=True)

    @mark_safe
    def uploads(self, obj):
        expenses = obj.uploads.filter(category=UploadCategoryChoices.EXPENSE).order_by('uploaded_on')
        revenues = obj.uploads.filter(category=UploadCategoryChoices.REVENUE).order_by('uploaded_on')
        total_expenses = len(expenses)
        total_revenues = len(revenues)

        def format_uploads(qs):
            html = ""
            first = True
            for u in qs:
                if not first:
                    html += ", "
                html += f"{u.report.upper()}"
                if u.status in UploadStatusChoices.get_error_status():
                    html += ' <span class="ui-icon ui-icon-alert" title="With error"></span>'
                elif u.status in UploadStatusChoices.get_in_progress_status():
                    html += ' <span class="ui-icon ui-icon-play" title="Importing"></span>'
                elif u.status == UploadStatusChoices.WAITING_REIMPORT:
                    html += ' <span class="ui-icon ui-icon-refresh" title="Waiting reimport"></span>'
                first = False
            return html

        headers = [_("Expenses: <strong>{total_expenses}</strong>".format(total_expenses=total_expenses)),
                   _("Revenues: <strong>{total_revenues}</strong>".format(total_revenues=total_revenues))]
        row = [
            [format_uploads(expenses), format_uploads(revenues)]
        ]

        return tabulate(row, headers=headers, tablefmt='unsafehtml')
    uploads.short_description = _("uploads")

    @mark_safe
    def uploads_with_error(self, obj):
        errors_count = obj.uploads.filter(status__in=UploadStatusChoices.get_error_status()).count()
        html = f"{errors_count}"
        if errors_count > 0:
            html += '&nbsp;&nbsp;<span class="ui-icon ui-icon-alert"></span>'
        return html
    uploads_with_error.short_description = _("uploads with error")

    def reimport_uploads(self, request, queryset):
        for budget in queryset:
            reimport_budget_uploads.delay(budget.id)
        messages.add_message(request, level=messages.WARNING,
                             message="Uploads from selected budgets are being reimported. "
                                     "Come back in a few minutes and refresh this page to check results.")

    def remove_uploads_with_error(self, request, queryset):
        for budget in queryset:
            budget.uploads.filter(status__in=UploadStatusChoices.get_error_status()).delete()
        messages.add_message(request, level=messages.SUCCESS,
                             message="Uploads removed with success.")


@admin.register(TransparencyIndex)
class TransparencyIndexAdmin(CountryPermissionMixin, admin.ModelAdmin):
    list_display = ('country', 'year', 'score_open_data', 'score_reports', 'score_data_quality', 'transparency_index',)
    list_editable = ('score_open_data', 'score_reports', 'score_data_quality', 'transparency_index',)
    list_filter = ('year', 'country', )
    fieldsets = (
        (_("Base info"), {
            'fields': ('country', 'year', )
        }),
        (_("Transparency Index"), {
            'fields': (('score_open_data', 'score_reports', 'score_data_quality', 'transparency_index'),),
        }),
    )


@admin.register(UploadLog)
class UploadLogAdmin(CountryPermissionMixin, admin.ModelAdmin):
    country_lookup_field = 'upload__budget__country'
    list_display = ('id', 'log_type', '_category_label', '_group', '_category_name', '_field', '_old_value',
                    '_new_value', 'upload', 'updated_by')
    list_filter = ('log_type',)
    readonly_fields = ('log_type', '_category_label', '_group', '_category_name', '_field', '_old_value', '_new_value',
                       'upload', 'updated_by', 'time')
    search_fields = ('field', 'category_name')
    ordering = ('time', 'id')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def lookup_allowed(self, lookup, value):
        if lookup in ('upload_id',):
            return True
        return super().lookup_allowed(lookup, value)

    def _category_label(self, obj):
        return obj.category.get_model_label()
    _category_label.short_description = _("category")

    def _group(self, obj):
        return obj.category.get_taxonomy_label()
    _group.short_description = _("group")

    def _category_name(self, obj):
        return obj.category_name
    _category_name.short_description = _("name")

    def _old_value(self, obj):
        if not obj.old_value:
            return "-"
        return raw_money_display(obj.old_value)
    _old_value.short_description = _("old value")

    def _new_value(self, obj):
        if not obj.new_value:
            return "-"
        return raw_money_display(obj.new_value)
    _new_value.short_description = _("new value")

    def _field(self, obj):
        if not obj.field:
            return "-"
        return obj.category.__class__._meta.get_field(obj.field).verbose_name
    _field.short_description = _("field")
