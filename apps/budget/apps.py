from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BudgetConfig(AppConfig):
    name = 'apps.budget'
    verbose_name = _("Budget")
