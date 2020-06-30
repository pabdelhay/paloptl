import codecs
import csv

from celery import task

from apps.budget.choices import UploadStatusChoices
from apps.budget.models import Upload


@task
def import_file(upload_id):
    upload = Upload.objects.get(id=upload_id)
    upload.status = UploadStatusChoices.VALIDATING
    upload.save()

    is_valid = upload.validate()
    if not is_valid:
        upload.status = UploadStatusChoices.VALIDATION_ERROR
        upload.save()
        return upload

    upload.file.seek(0)
    is_valid = upload.do_import()
    if not is_valid:
        upload.status = UploadStatusChoices.IMPORT_ERROR
        upload.save()
        return upload

    upload.status = UploadStatusChoices.SUCCESS
    upload.save()
    return upload
