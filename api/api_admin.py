from rest_framework import viewsets, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.account.tasks import test_celery


class BudgetUploadSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=('organic', 'functional'))
    category = serializers.CharField(max_length=255)
    subcategory = serializers.CharField(required=False, max_length=255)

    budget_operation = serializers.FloatField(required=False, allow_null=True)
    budget_investment = serializers.FloatField(required=False, allow_null=True)
    budget_aggregated = serializers.FloatField(required=False, allow_null=True)
    execution_operation = serializers.FloatField(required=False, allow_null=True)
    execution_investment = serializers.FloatField(required=False, allow_null=True)
    execution_aggregated = serializers.FloatField(required=False, allow_null=True)


class AdminViewset(viewsets.ViewSet):
    """
    Admin actions
    """
    permission_classes = [permissions.IsAdminUser]

    @action(methods=['get'], detail=False)
    def test_celery_works(self, request, pk=None):
        test_celery.delay()
        return Response('ok')

