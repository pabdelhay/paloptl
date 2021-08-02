from django.contrib.admin.options import get_content_type_for_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.budget.choices import ExpenseGroupChoices
from apps.budget.models import Function, Expense, Agency, Budget


class Command(BaseCommand):
    help = "Migrate budget accounts to new Revenue/Expense database structure."

    def handle(self, *args, **options):
        budget_filter = None
        expense_ct = get_content_type_for_model(Expense)

        def migrate_budget_account(budget_account_class, group, budget_id):
            base_qs = budget_account_class.objects.all().select_related('budget')
            if budget_id:
                base_qs = base_qs.filter(budget_id=budget_id)
            migrated_ids = Expense.objects.filter(group=group,
                                                  content_type__model=budget_account_class._meta.model_name)\
                .values_list('object_id', flat=True)
            base_qs = base_qs.exclude(id__in=migrated_ids)

            for ba in base_qs.order_by('level'):
                with transaction.atomic():
                    print(f"Updating {group} {ba.id} - {ba.name} from budget {ba.budget.id}... ", end='')
                    expense = ba.migrated_to.first()
                    if not expense:
                        new_parent = None
                        if ba.parent:
                            new_parent = ba.parent.migrated_to.first()
                            if not new_parent:
                                raise Exception(f"Parent for {ba.id} - {ba.name} ({ba.group}) not created yet")
                        expense = Expense.objects.create(
                            budget=ba.budget,
                            group=group,
                            name=ba.name,
                            code=ba.code,
                            parent=new_parent,
                            initial_budget_investment=ba.initial_budget_investment,
                            initial_budget_operation=ba.initial_budget_operation,
                            initial_budget_aggregated=ba.initial_budget_aggregated,
                            budget_investment=ba.budget_investment,
                            budget_operation=ba.budget_operation,
                            budget_aggregated=ba.budget_aggregated,
                            execution_investment=ba.execution_investment,
                            execution_operation=ba.execution_operation,
                            execution_aggregated=ba.execution_aggregated,
                            inferred_values=ba.inferred_values,
                            inferred_fields=ba.inferred_fields,
                            last_update=ba.last_update,
                            migrated_from=ba
                        )
                    ba.upload_logs.all().update(content_type=expense_ct, object_id=expense.id)
                    print("OK")

        budget_qs = Budget.objects.all()
        if budget_filter:
            budget_qs = budget_qs.filter(id=budget_filter)
        for budget in budget_qs:
            print(f"=== Migrating Budget {budget.id} - {budget.country.name} ({budget.year}) ===")
            migrate_budget_account(Function, ExpenseGroupChoices.FUNCTIONAL, budget_id=budget.id)
            migrate_budget_account(Agency, ExpenseGroupChoices.ORGANIC, budget_id=budget.id)

            print("Updating inferred values...", end=' ')
            budget.update_inferred_values()
            print("OK")

            print("Updating json files...", end=' ')
            budget.update_json_files()
            print("OK")

        print("=== FINISHED ===")
