from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.account.tasks import test_celery


class AdminViewset(viewsets.ViewSet):
    """
    Admin actions
    """
    permission_classes = [permissions.IsAdminUser]

    @action(methods=['get'], detail=False)
    def test_celery_works(self, request, pk=None):
        test_celery.delay()
        return Response('ok')

