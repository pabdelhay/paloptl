from django.contrib import admin


class CountryPermissionMixin(object):
    """
    Filter admin lists only for instances related to user's country.
    """
    country_lookup_field = 'country'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Get a form Field for a ForeignKey.
        """
        form_field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name != 'country':
            return form_field

        user = request.user
        user_country = user.profile.country
        if user.is_superuser:
            return form_field

        form_field.queryset = form_field.queryset.filter(id=user_country.id)
        form_field.initial = user_country
        form_field.disabled = True

        return form_field

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

