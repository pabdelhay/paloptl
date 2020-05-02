from django.contrib import admin

from apps.geo.models import Country


@admin.register(Country)
class AuthorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
