from celery import task
from django.utils.translation import gettext_lazy as _
from sentry_sdk import capture_exception

from apps.budget.choices import UploadStatusChoices
from apps.budget.models import Upload


@task
def import_file(upload_id):
    upload = Upload.objects.get(id=upload_id)
    upload.status = UploadStatusChoices.VALIDATING
    upload.save()

    # Validation
    is_valid = upload.validate()
    if not is_valid:
        upload.status = UploadStatusChoices.VALIDATION_ERROR
        upload.save()
        return upload

    # Import
    upload.file.seek(0)
    is_valid = upload.do_import()
    if not is_valid:
        upload.status = UploadStatusChoices.IMPORT_ERROR
        upload.save()
        return upload

    try:
        upload.budget.update_inferred_values()
        upload.status = UploadStatusChoices.SUCCESS
    except Exception as e:
        capture_exception(e)
        upload.status = UploadStatusChoices.IMPORT_ERROR
        upload.errors.append(_("An unexpected error occurred while updating inferred values from the upload. "
                               "Please contact the dev team."))

    upload.save()
