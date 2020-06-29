from django.contrib import admin

from apps.budget.choices import UploadStatusChoices
from apps.budget.models import Upload, Budget
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
                instance.status = UploadStatusChoices.VALIDATING
            instance.save()
            if is_new:
                import_file.delay(instance.id)
        formset.save_m2m()
