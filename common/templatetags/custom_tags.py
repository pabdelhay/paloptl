from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def get_menu_title(user):
    if user.profile.country is not None:
        return f'<img class="header-flag" src="{user.profile.country.flag.url}" /> {user.profile.country.name}'
    else:
        return "Menu"
