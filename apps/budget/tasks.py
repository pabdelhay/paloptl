import re

from celery import task
from django.utils.translation import gettext_lazy as _
from sentry_sdk import capture_exception

from apps.budget.choices import UploadStatusChoices


@task
def import_file(upload_id):
    from apps.budget.models import Upload
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
        upload.errors.append(_("An unexpected error occurred while validating the upload. Please contact the dev "
                               "team informing the following error message:<br><i>{error}</i>").format(error=str(e)))
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
        upload.errors.append(_("An unexpected error occurred while executing the import. Please contact the dev "
                               "team informing the following error message:<br><i>{error}</i>").format(error=str(e)))
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
        upload.errors.append(_("An unexpected error occurred while updating inferred values. Please contact the dev "
                               "team informing the following error message:<br><i>{error}</i>").format(error=str(e)))
        upload.save()
        return upload

    # Update JSON files
    try:
        upload.budget.update_json_files()
    except Exception as e:
        capture_exception(e)
        upload.status = UploadStatusChoices.IMPORT_ERROR
        upload.errors.append(_("An unexpected error occurred while creating the cache file. Please contact the dev "
                               "team informing the following error message:<br><i>{error}</i>").format(error=str(e)))
        upload.save()
        return upload

    upload.save()

    # Update CSV file
    # Running async since the csv file is not crucial for the country page. Preventing any unmapped error.
    make_budget_csv_file.delay(upload.budget_id)

    return upload


@task
def make_budget_csv_file(budget_id):
    """
    Make a CSV file with all data from budget.
    :param budget_id: int
    """
    from apps.budget.models import Budget
    budget = Budget.objects.get(id=budget_id)
    budget.update_csv_file()


@task
def reimport_budget_uploads(budget_id, include_uploads_with_error=False):
    """
    - Remove all BudgetAccount data from a Budget
    - Remove all UploadLog from a Budget
    - Set Budget's Uploads status to waiting reimport
    - Execute import_file() for each Budget's Upload in order of uploaded
    :param upload_id: int
    """
    from apps.budget.models import Budget, UploadLog
    budget = Budget.objects.get(id=budget_id)
    print(f"----- Reimporting all uploads from Budget #{budget.id} {budget.country.name} {budget.year} -----")

    # 1. Remove all BudgetAccount data
    budget.functions.all().delete()
    budget.agencies.all().delete()

    filters = {'status__in': UploadStatusChoices.get_success_status()}
    if include_uploads_with_error:
        filters['status__in'] = UploadStatusChoices.get_success_status() + UploadStatusChoices.get_error_status()
    upload_qs = budget.uploads.filter(**filters)
    upload_ids = [u.id for u in upload_qs]

    # 2. Remove all UploadLog
    UploadLog.objects.filter(upload_id__in=upload_ids).delete()

    # 3. Set Budget's Uploads status to waiting reimport
    upload_qs.update(status=UploadStatusChoices.WAITING_REIMPORT, errors=[])

    # 4. Execute import_file() for each Budget's Upload
    for upload in budget.uploads.filter(status=UploadStatusChoices.WAITING_REIMPORT).order_by('uploaded_on'):
        print(f"Reimporting Upload #{upload.id}... ", end='')
        upload = import_file(upload_id=upload.id)
        upload.refresh_from_db()
        if upload.status not in UploadStatusChoices.get_success_status():
            print(f"ERROR")
            for error in upload.errors:
                error = re.sub('<[^<]+?>', '', error)
                print(f"    {error}")
            break  # Every upload must be imported in order, so we break loop here.
        else:
            print(f"OK")

    print(f"=== FINISHED ===")
