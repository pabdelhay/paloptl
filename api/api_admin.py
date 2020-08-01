from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.account.tasks import test_celery
from apps.budget.choices import UploadStatusChoices
from apps.budget.models import Upload
from apps.geo.models import Country


class BudgetUploadSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=('organic', 'functional'))
    category = serializers.CharField(max_length=255)
    subcategory = serializers.CharField(required=False, allow_null=True, max_length=255)

    budget_operation = serializers.FloatField(required=False, allow_null=True)
    budget_investment = serializers.FloatField(required=False, allow_null=True)
    budget_aggregated = serializers.FloatField(required=False, allow_null=True)
    execution_operation = serializers.FloatField(required=False, allow_null=True)
    execution_investment = serializers.FloatField(required=False, allow_null=True)
    execution_aggregated = serializers.FloatField(required=False, allow_null=True)


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
            request.session.pop('upload_in_progress')
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
