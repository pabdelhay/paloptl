from django import template
from django.utils import timezone

from apps.budget.models import Budget
from apps.geo.models import Country

register = template.Library()


@register.simple_tag
def get_latest_budgets(user):
    current_year = timezone.now().year
    base_qs = Budget.objects.filter(year__gte=current_year - 1).order_by('country__name', '-year')
    if user.profile.country is not None:
        base_qs = base_qs.filter(country=user.profile.country)
    return base_qs


@register.simple_tag
def get_current_budget(user):
    current_year = timezone.now().year
    base_qs = Budget.objects.filter(year=current_year)
    if user.profile.country is not None:
        base_qs = base_qs.filter(country=user.profile.country)
    return base_qs.first()


@register.simple_tag
def get_countries():
    return Country.objects.all().order_by('name')
