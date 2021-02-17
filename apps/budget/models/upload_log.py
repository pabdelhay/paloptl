from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.budget.choices import LogTypeChoices


class UploadLog(models.Model):
    upload = models.ForeignKey('budget.Upload', verbose_name=_("upload"), related_name='logs',
                               on_delete=models.CASCADE, editable=False)
    log_type = models.CharField(max_length=20, choices=LogTypeChoices.choices, editable=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, editable=False)
    object_id = models.PositiveIntegerField(editable=False)
    category = GenericForeignKey('content_type', 'object_id')
    category_name = models.CharField(verbose_name=_("category"), max_length=255, null=True, blank=True, editable=False)

    field = models.CharField(verbose_name=_("field"), max_length=40, null=True, blank=True, editable=False)
    old_value = models.FloatField(verbose_name=_("old value"), null=True, blank=True, editable=False)
    new_value = models.FloatField(verbose_name=_("new value"), null=True, blank=True, editable=False)

    time = models.DateTimeField(verbose_name=_("time"), auto_now_add=True, editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("updated by"), on_delete=models.PROTECT,
                                   editable=False)

    def __str__(self):
        return f"{self.get_log_type_display()}"
