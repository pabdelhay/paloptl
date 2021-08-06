from django.core.management.base import BaseCommand

from apps.budget.models import Budget


class Command(BaseCommand):
    help = "Update all budgets: csv, json and inferred values."

    def handle(self, *args, **options):
        for budget in Budget.objects.all():
            print(f"Updating budget {str(budget)}... ", end='')
            budget.update_inferred_values()
            budget.update_json_files()
            budget.update_csv_file()
            print("OK")
