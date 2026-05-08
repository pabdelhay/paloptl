from modeltranslation.translator import TranslationOptions, translator

from apps.budget.models import Attachment


class AttachmentTranslationOptions(TranslationOptions):
    fields = ('file', 'thumbnail', 'title')


translator.register(Attachment, AttachmentTranslationOptions)
