from django.core.management.base import BaseCommand

from apps.budget.models import Budget


class Command(BaseCommand):
    help = "Update all budgets: csv, json and inferred values."

    def add_arguments(self, parser):
        parser.add_argument('--country', type=str)

    def handle(self, *args, **options):
        qs = Budget.objects.all()
        if options['country']:
            qs = qs.filter(country__slug=options['country'])

        for budget in qs:
            print(f"Updating budget {str(budget)}... ", end='')
            budget.update_inferred_values()
            budget.update_json_files()
            budget.update_csv_file()
            print("OK")
