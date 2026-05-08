from django.db import models
from django.utils.translation import gettext_lazy as _


class Attachment(models.Model):
    title = models.CharField(verbose_name=_("title"), max_length=255, blank=True)
    file = models.FileField(verbose_name=_("file"), upload_to='attachments/files', null=True, blank=True)
    thumbnail = models.ImageField(
        verbose_name=_("thumbnail"), upload_to='attachments/thumbnails', null=True, blank=True
    )
    is_visible = models.BooleanField(verbose_name=_("is visible"), default=True)

    def __str__(self):
        return self.title or str(self.pk)

    class Meta:
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")
        ordering = ['id']
