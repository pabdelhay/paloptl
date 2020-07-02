from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin

from apps.budget.choices import UploadStatusChoices
from apps.budget.models import Upload, Budget
from apps.budget.models.agency import Agency
from apps.budget.models.function import Function
from apps.budget.tasks import import_file
from common.admin import CountryPermissionMixin


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


class BudgetAccountInline(admin.TabularInline):
    extra = 0
    readonly_fields = ('get_level_0_taxonomy', 'get_level_1_taxonomy', 'last_update')
    fields = ('get_level_0_taxonomy', 'get_level_1_taxonomy', 'budget_investment', 'budget_operation',
              'budget_aggregated', 'execution_investment', 'execution_operation', 'execution_aggregated', 'last_update')


class FunctionInline(BudgetAccountInline):
    model = Function

    def get_level_0_taxonomy(self, obj):
        return obj.parent.name if obj.parent else obj.name
    get_level_0_taxonomy.short_description = Agency.get_taxonomy(level=0)

    def get_level_1_taxonomy(self, obj):
        return obj.name if obj.parent else ""
    get_level_1_taxonomy.short_description = Agency.get_taxonomy(level=1)


class AgencyInline(BudgetAccountInline):
    model = Agency

    def get_level_0_taxonomy(self, obj):
        return obj.parent.name if obj.parent else obj.name
    get_level_0_taxonomy.short_description = Agency.get_taxonomy(level=0)

    def get_level_1_taxonomy(self, obj):
        return obj.name if obj.parent else ""
    get_level_1_taxonomy.short_description = Agency.get_taxonomy(level=1)


@admin.register(Budget)
class BudgetAdmin(CountryPermissionMixin, admin.ModelAdmin):
    inlines = (UploadInline, FunctionInline, AgencyInline)
    list_display = ('country', 'year')

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
                async_task = import_file.delay(instance.id)
                if async_task.status == 'SUCCESS':
                    # For easter execution of import_file (synchronous)
                    instance.refresh_from_db()
                    instance.save()
        formset.save(commit=True)


class BudgetAccountAdmin(CountryPermissionMixin, MPTTModelAdmin):
    country_lookup_field = 'budget__country'
    list_display = ('country', 'year', 'get_level_0_taxonomy', 'get_level_1_taxonomy', 'budget_investment',
                    'budget_operation', 'budget_aggregated', 'execution_investment', 'execution_operation',
                    'execution_aggregated', 'last_update')
    list_filter = ('budget',)

    def country(self, obj):
        return obj.budget.country.name
    country.short_description = _("country")

    def year(self, obj):
        return obj.budget.year
    year.short_description = _("year")


@admin.register(Agency)
class AgencyAdmin(BudgetAccountAdmin):
    def get_level_0_taxonomy(self, obj):
        return obj.parent.name if obj.parent else obj.name
    get_level_0_taxonomy.short_description = Agency.get_taxonomy(level=0)

    def get_level_1_taxonomy(self, obj):
        return obj.name if obj.parent else ""
    get_level_1_taxonomy.short_description = Agency.get_taxonomy(level=1)


@admin.register(Function)
class FunctionAdmin(BudgetAccountAdmin):
    def get_level_0_taxonomy(self, obj):
        return obj.parent.name if obj.parent else obj.name
    get_level_0_taxonomy.short_description = Function.get_taxonomy(level=0)

    def get_level_1_taxonomy(self, obj):
        return obj.name if obj.parent else ""
    get_level_1_taxonomy.short_description = Function.get_taxonomy(level=1)
