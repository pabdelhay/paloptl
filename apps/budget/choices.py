from django.db import models
from django.utils.translation import gettext_lazy as _


class UploadReportChoices(models.TextChoices):
    OGE = 'oge', _("OGE - Orçamento Geral do Estado")
    REO = 'reo', _("REO - Relatório de Execução Orçamentária")
    CGE = 'cge', _("CGE - Conta Geral do Estado")
