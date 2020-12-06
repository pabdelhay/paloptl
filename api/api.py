from django.conf import settings
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
    label = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name', 'initial_budget_investment', 'initial_budget_operation', 'initial_budget_aggregated',
                  'budget_investment', 'budget_operation', 'budget_aggregated',
                  'execution_investment', 'execution_operation', 'execution_aggregated',
                  'last_update', 'children', 'label', 'color', 'level', 'tree_id')

    def get_label(self, obj):
        return obj.get_taxonomy_label()

    def get_color(self, obj):
        color_index = 0
        execution_value = obj.execution_aggregated or 0

        # TODO: REMOVE ME
        if not obj.budget_aggregated:
            return settings.TREEMAP_EXECUTION_COLORS[color_index]

        execution_percent = execution_value / obj.budget_aggregated
        if 0.2 < execution_percent <= 0.4:
            color_index = 1
        if 0.4 < execution_percent <= 0.6:
            color_index = 2
        elif 0.6 < execution_percent <= 0.8:
            color_index = 3
        if 0.8 < execution_percent:
            color_index = 4
        return settings.TREEMAP_EXECUTION_COLORS[color_index]


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
