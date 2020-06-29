import codecs
import csv

from celery import task

from apps.budget.choices import UploadStatusChoices
from apps.budget.models import Upload


@task
def import_file(upload_id):
    upload = Upload.objects.get(id=upload_id)
    upload.validate()

    # TODO: VALIDATE AND IMPORT

    upload.status = UploadStatusChoices.SUCCESS
    upload.save()
