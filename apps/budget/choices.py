from django.db import models
from django.utils.translation import gettext_lazy as _


class UploadReportChoices(models.TextChoices):
    OGE = 'oge', _("OGE - Orçamento Geral do Estado")
    REO = 'reo', _("REO - Relatório de Execução Orçamentária")
    CGE = 'cge', _("CGE - Conta Geral do Estado")


class UploadStatusChoices(models.TextChoices):
    VALIDATING = 'validating', _("Validating")
    IMPORTING = 'importing', _("Importing")
    SUCCESS = 'success', _("Success")
    VALIDATION_ERROR = 'validation_error', _("Validation error")
    IMPORT_ERROR = 'import_error', _("Import error")
