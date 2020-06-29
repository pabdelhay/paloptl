from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _

from apps.account.models import Profile
from common.admin import CountryPermissionMixin


class ProfileInline(CountryPermissionMixin, admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(CountryPermissionMixin, UserAdmin):
    country_lookup_field = 'profile__country'
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser', 'country')
    list_select_related = ('profile',)

    # For non-superusers
    staff_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'groups'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def change_view(self, request, *args, **kwargs):
        # For non-superuser
        if not request.user.is_superuser:
            try:
                self.fieldsets = self.staff_fieldsets
                response = super().change_view(request, *args, **kwargs)
            finally:
                # Reset fieldsets to its original value
                self.fieldsets = UserAdmin.fieldsets
            return response
        else:
            return super().change_view(request, *args, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.save()
        user_country = request.user.profile.country
        if not change and user_country is not None:
            obj.profile.country = user_country
            obj.profile.save()

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

    def country(self, obj):
        if obj.profile:
            return obj.profile.country
        return ""
    country.short_description = 'país'


admin.site.site_header = "PALOP-TL CSO online budget platform"
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)