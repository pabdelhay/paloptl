from django.core.management.base import BaseCommand

from apps.budget.models import Budget


class Command(BaseCommand):
    help = "Update all budgets json files."

    def handle(self, *args, **options):
        for budget in Budget.objects.all():
            print(f"Updating budget {str(budget)}... ", end='')
            budget.update_json_files()
            print("OK")
