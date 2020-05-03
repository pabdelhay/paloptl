from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

from apps.account.models import Profile
from common.admin import CountryPermissionMixin


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(CountryPermissionMixin, UserAdmin):
    country_lookup_field = 'profile__country'
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser', 'country')
    list_select_related = ('profile',)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

    def country(self, obj):
        if obj.profile:
            return obj.profile.country
        return ""


admin.site.site_header = "PALOP-TL CSO online budget platform"
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)