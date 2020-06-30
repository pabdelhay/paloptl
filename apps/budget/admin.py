from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin

from apps.budget.models import Upload, Budget
from apps.budget.models.agency import Agency
from apps.budget.models.function import Function
from apps.budget.tasks import import_file
from common.admin import CountryPermissionMixin


class UploadInline(admin.TabularInline):
    model = Upload
    extra = 1
    readonly_fields = ('status', 'uploaded_by', 'uploaded_on')


@admin.register(Budget)
class BudgetAdmin(CountryPermissionMixin, admin.ModelAdmin):
    inlines = (UploadInline, )
    list_display = ('country', 'year')

    def save_formset(self, request, form, formset, change):
        if formset.model != Upload:
            return super().save_formset(request, form, formset, change)

        instances = formset.save(commit=False)
        for instance in instances:
            is_new = not instance.pk
            if is_new:
                instance.uploaded_by = request.user
            instance.save()
            if is_new:
                async_task = import_file.delay(instance.id)
                if async_task.status == 'SUCCESS':
                    # For easter execution of import_file (synchronous)
                    upload = async_task.result
                    instance.status = upload.status
                    instance.errors = upload.errors
                    instance.log = upload.log
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
        return obj.name if obj.parent else None
    get_level_1_taxonomy.short_description = Agency.get_taxonomy(level=1)


@admin.register(Function)
class FunctionAdmin(BudgetAccountAdmin):
    def get_level_0_taxonomy(self, obj):
        return obj.parent.name if obj.parent else obj.name
    get_level_0_taxonomy.short_description = Function.get_taxonomy(level=0)

    def get_level_1_taxonomy(self, obj):
        return obj.name if obj.parent else None
    get_level_1_taxonomy.short_description = Function.get_taxonomy(level=1)
