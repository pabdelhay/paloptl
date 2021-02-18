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
    try:
        is_valid = upload.validate()
    except Exception as e:
        # Catching unexpected exception to avoid status stuck in 'validating'.
        capture_exception(e)
        upload.status = UploadStatusChoices.VALIDATION_ERROR
        upload.errors.append(_("An unexpected error occurred while validating the upload. "
                               "Please contact the dev team."))
        upload.save()
        return upload

    if not is_valid:
        upload.status = UploadStatusChoices.VALIDATION_ERROR
        upload.save()
        return upload

    # Import
    try:
        upload.file.seek(0)
        is_valid = upload.do_import()
    except Exception as e:
        # Catching unexpected exception to avoid status stuck in 'validating'.
        capture_exception(e)
        upload.status = UploadStatusChoices.IMPORT_ERROR
        upload.errors.append(_("An unexpected error occurred while executing the import. Please contact the dev team."))
        upload.save()
        return upload

    if not is_valid:
        upload.status = UploadStatusChoices.IMPORT_ERROR
        upload.save()
        return upload

    upload.status = UploadStatusChoices.SUCCESS

    # Update inferred values
    try:
        upload.budget.update_inferred_values()
    except Exception as e:
        capture_exception(e)
        upload.status = UploadStatusChoices.IMPORT_ERROR
        upload.errors.append(_("An unexpected error occurred while updating inferred values from the upload. "
                               "Please contact the dev team."))
        upload.save()
        return upload

    # Update JSON files
    try:
        upload.budget.update_json_files()
    except Exception as e:
        capture_exception(e)
        upload.status = UploadStatusChoices.IMPORT_ERROR
        upload.errors.append(_("An unexpected error occurred while creating the JSON file for the budget. "
                               "Please contact the dev team."))
        upload.save()
        return upload

    upload.save()
