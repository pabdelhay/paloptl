from django.contrib import admin


class CountryPermissionMixin(admin.ModelAdmin):
    """
    Filter admin lists only for instances related to user's country.
    """
    country_lookup_field = 'country'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        user_country = user.profile.country
        if user.is_superuser and not user_country:
            return qs

        filters = {
            self.country_lookup_field: user_country
        }
        return qs.filter(**filters)
