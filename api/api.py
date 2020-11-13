from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_recursive.fields import RecursiveField

from apps.budget.models import Budget, Function, Agency


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ('id', 'year', 'currency')


class BudgetAccountSerializer(serializers.ModelSerializer):
    children = serializers.ListSerializer(child=RecursiveField())

    class Meta:
        fields = ('id', 'name', 'initial_budget_investment', 'initial_budget_operation', 'initial_budget_aggregated',
                  'budget_investment', 'budget_operation', 'budget_aggregated',
                  'execution_investment', 'execution_operation', 'execution_aggregated',
                  'last_update', 'children')


class FunctionSerializer(BudgetAccountSerializer):
    class Meta:
        model = Function
        fields = BudgetAccountSerializer.Meta.fields


class AgencySerializer(BudgetAccountSerializer):
    class Meta:
        model = Agency
        fields = BudgetAccountSerializer.Meta.fields


class BudgetViewset(ReadOnlyModelViewSet):
    model = Budget
    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()

    @action(detail=True)
    def functions(self, request, pk=None):
        budget = self.get_object()
        qs = Function.objects.filter(budget=budget, level=0)
        serializer = FunctionSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def agencies(self, request, pk=None):
        budget = self.get_object()
        qs = Agency.objects.filter(budget=budget, level=0)
        serializer = AgencySerializer(qs, many=True)
        return Response(serializer.data)
