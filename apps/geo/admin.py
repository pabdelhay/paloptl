from django.contrib import admin
from apps.geo.models import Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency')
    prepopulated_fields = {'slug': ('name',)}
