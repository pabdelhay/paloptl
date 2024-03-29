from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.account.tasks import test_celery
from apps.budget.choices import UploadStatusChoices, RevenueGroupChoices, ExpenseGroupChoices
from apps.budget.models import Upload
from apps.budget.tasks import reimport_budget_uploads, make_budget_csv_file
from apps.geo.models import Country


class BudgetUploadSerializer(serializers.Serializer):
    # report_type is DEPRECATED. Use group instead.
    report_type = serializers.ChoiceField(choices=ExpenseGroupChoices.choices + RevenueGroupChoices.choices,
                                          required=False, allow_null=True)
    group = serializers.ChoiceField(choices=ExpenseGroupChoices.choices + RevenueGroupChoices.choices)

    category = serializers.CharField(max_length=255)
    subcategory = serializers.CharField(max_length=255, required=False, allow_null=True)
    category_code = serializers.CharField(max_length=30, required=False, allow_null=True)
    subcategory_code = serializers.CharField(max_length=30, required=False, allow_null=True)

    budget_operation = serializers.FloatField(required=False, allow_null=True)
    budget_investment = serializers.FloatField(required=False, allow_null=True)
    budget_aggregated = serializers.FloatField(required=False, allow_null=True)
    execution_operation = serializers.FloatField(required=False, allow_null=True)
    execution_investment = serializers.FloatField(required=False, allow_null=True)
    execution_aggregated = serializers.FloatField(required=False, allow_null=True)

    def validate(self, data):
        if not data.get('group') and not data.get('report_type'):
            raise serializers.ValidationError({'group': _("Must set 'group' field.")})
        return data


class ExpenseUploadSerializer(BudgetUploadSerializer):
    # 'report_type' maps to 'Expense.group'
    report_type = serializers.ChoiceField(choices=ExpenseGroupChoices.choices, required=False, allow_null=True)
    group = serializers.ChoiceField(choices=ExpenseGroupChoices.choices, required=False, allow_null=True)


class RevenueUploadSerializer(BudgetUploadSerializer):
    # 'report_type' maps to 'Revenue.group'
    report_type = serializers.ChoiceField(choices=RevenueGroupChoices.choices, required=False, allow_null=True)
    group = serializers.ChoiceField(choices=RevenueGroupChoices.choices, required=False, allow_null=True)


class UploadInProgressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Upload
        fields = ('id', 'status', 'get_report_display', 'budget_id')


class AdminViewset(viewsets.ViewSet):
    """
    Admin actions
    """
    permission_classes = [permissions.IsAdminUser]

    @action(methods=['get'], detail=False)
    def test_celery_works(self, request, pk=None):
        request.session['upload_in_progress'] = True
        test_celery.delay()
        return Response('ok')

    @action(methods=['get'], detail=True)
    def check_in_progress_upload(self, request, pk=None):
        upload_id = pk
        if not upload_id:
            return Response({})

        try:
            upload = Upload.objects.get(id=upload_id)
        except Upload.DoesNotExist:
            request.session.pop('upload_in_progress', None)
            return Response({})

        if upload.status not in UploadStatusChoices.get_in_progress_status():
            # Found in progress upload an it's already finished validating/importing.
            request.session.pop('upload_in_progress', None)

        serializer = UploadInProgressSerializer(instance=upload, context={'request': request})
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def get_currency_from_country(self, request, pk=None):
        country_id = pk
        country = Country.objects.get(id=country_id)
        return Response(country.currency)

    @action(methods=['post'], detail=True)
    def reimport_budget(self, request, pk=None):
        budget_id = pk
        reimport_budget_uploads.delay(budget_id=budget_id)
        return Response('reimporting')

    @action(methods=['post'], detail=True)
    def update_budget_output_file(self, request, pk=None):
        budget_id = pk
        make_budget_csv_file.delay(budget_id=budget_id)
        return Response('updating')
