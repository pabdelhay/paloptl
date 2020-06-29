from django.contrib import admin

from apps.budget.models import Upload, Budget
from common.admin import CountryPermissionMixin


class UploadInline(admin.TabularInline):
    model = Upload
    extra = 1
    can_delete = False
    readonly_fields = ('uploaded_by', 'uploaded_on')


@admin.register(Budget)
class BudgetAdmin(CountryPermissionMixin, admin.ModelAdmin):
    inlines = (UploadInline, )
    list_display = ('country', 'year')

    def save_formset(self, request, form, formset, change):
        if formset.model != Upload:
            return super().save_formset(request, form, formset, change)
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:
                instance.uploaded_by = request.user
            instance.save()
        formset.save_m2m()
