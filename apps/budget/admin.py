from django.contrib import admin

from apps.budget.models import Upload, Budget
from common.admin import CountryPermissionMixin


class UploadInline(admin.TabularInline):
    model = Upload
    extra = 1
    can_delete = False


@admin.register(Budget)
class BudgetAdmin(CountryPermissionMixin, admin.ModelAdmin):
    inlines = (UploadInline, )
    list_display = ('country', 'year')

