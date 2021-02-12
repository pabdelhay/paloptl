from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_admin_inline_paginator.admin import TabularInlinePaginated

from apps.budget.choices import UploadStatusChoices
from apps.budget.models import Upload, Budget
from apps.budget.models.agency import Agency
from apps.budget.models.function import Function
from apps.budget.tasks import import_file
from common.admin import CountryPermissionMixin
from common.methods import raw_money_display


class UploadInline(admin.TabularInline):
    model = Upload
    extra = 1
    fields = ('file', 'report', 'status', 'get_log', 'uploaded_by', 'uploaded_on')
    readonly_fields = ('status', 'uploaded_by', 'uploaded_on', 'get_log')

    @mark_safe
    def get_log(self, obj):
        if not obj.id:
            return "-"
        link_text = _("Log") + f" ({len(obj.log)})"
        log = "<br>".join(obj.log) if obj.log else ""
        if obj.status in UploadStatusChoices.get_error_status():
            link_text = _("Errors") + f" ({len(obj.errors)})"
            log = "<br>".join(obj.errors)

        html = f'<div class="upload-log-wrapper">' \
               f'   <input type="hidden" name="status-{obj.id}" class="status-input" value="{obj.status}">'
        if obj.status != UploadStatusChoices.VALIDATING:
            html += \
               f'   <div class="upload-log" id="upload-dialog-{obj.id}">{log}</div>' \
               f'   <a href="#" class="log-link" data-upload_id="{obj.id}">{link_text}</a>'
        else:
            html += f'-'
        html += f'</div>'
        return html
    get_log.short_description = "log"


class BudgetAccountInline(TabularInlinePaginated):
    extra = 0
    per_page = 50
    readonly_fields = ('code', 'get_group_taxonomy', 'get_subgroup_taxonomy', 'last_update',
                       'get_budget_investment', 'get_budget_operation', 'get_budget_aggregated',
                       'get_execution_investment', 'get_execution_operation', 'get_execution_aggregated')
    fields = ('code', 'get_group_taxonomy', 'get_subgroup_taxonomy', 'get_budget_investment', 'get_budget_operation',
              'get_budget_aggregated', 'get_execution_investment', 'get_execution_operation',
              'get_execution_aggregated', 'last_update')
    classes = ['collapse']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj):
        return request.user.is_superuser

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
                      .format(raw_money_display(inferred_value)))

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


class FunctionInline(BudgetAccountInline):
    model = Function

    def get_group_taxonomy(self, obj):
        return obj.parent.name if obj.parent else obj.name
    get_group_taxonomy.short_description = Function.get_taxonomy(level=0)

    def get_subgroup_taxonomy(self, obj):
        return obj.name if obj.parent else ""
    get_subgroup_taxonomy.short_description = Function.get_taxonomy(level=1)


class AgencyInline(BudgetAccountInline):
    model = Agency

    def get_group_taxonomy(self, obj):
        return obj.parent.name if obj.parent else obj.name
    get_group_taxonomy.short_description = Agency.get_taxonomy(level=0)

    def get_subgroup_taxonomy(self, obj):
        return obj.name if obj.parent else ""
    get_subgroup_taxonomy.short_description = Agency.get_taxonomy(level=1)


@admin.register(Budget)
class BudgetAdmin(CountryPermissionMixin, admin.ModelAdmin):
    fieldsets = (
        ("Base info", {
            'fields': ('country', 'year', 'currency',)
        }),
        ("Transparency Index", {
            'fields': (('score_open_data', 'score_reports', 'score_data_quality', 'transparency_index'),),
        }),
    )
    inlines = (UploadInline, FunctionInline, AgencyInline)  # Commented because of large data timeouts.
    list_display = ('country', 'year', 'transparency_index')
    list_filter = ('year', )
    readonly_fields = ('currency', )

    def save_formset(self, request, form, formset, change):
        if formset.model != Upload:
            return super().save_formset(request, form, formset, change)

        instances = formset.save(commit=False)
        for instance in instances:
            is_new = not instance.pk
            if is_new:
                instance.uploaded_by = request.user
                instance.status = UploadStatusChoices.VALIDATING
            instance.save()
            if is_new:
                request.session['upload_in_progress'] = instance.id
                async_task = import_file.delay(instance.id)
                if async_task.status == 'SUCCESS':
                    # For easter execution of import_file (synchronous on dev mode)
                    instance.refresh_from_db()
                    instance.save()
                elif async_task.status == 'FAILURE':
                    # TODO: Resolve unmapped errors.
                    pass
        formset.save(commit=True)
