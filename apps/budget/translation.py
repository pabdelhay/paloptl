from modeltranslation.translator import TranslationOptions, translator

from apps.budget.models import Attachment, TransparencyIndex


class AttachmentTranslationOptions(TranslationOptions):
    fields = ('file', 'thumbnail', 'title')


class TransparencyIndexTranslationOptions(TranslationOptions):
    fields = ('report',)


translator.register(Attachment, AttachmentTranslationOptions)
translator.register(TransparencyIndex, TransparencyIndexTranslationOptions)