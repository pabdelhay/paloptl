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
    WAITING_REIMPORT = 'waiting_reimport', _("Waiting reimport")

    @classmethod
    def get_error_status(cls):
        return [cls.VALIDATION_ERROR, cls.IMPORT_ERROR]

    @classmethod
    def get_in_progress_status(cls):
        return [cls.VALIDATING, cls.IMPORTING]

    @classmethod
    def get_success_status(cls):
        return [cls.SUCCESS]


class LogTypeChoices(models.TextChoices):
    NEW_CATEGORY = 'new_category', _("new category")
    UPDATE = 'update', _("update")
