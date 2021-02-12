from django.conf import settings
from django.db import models
from django.db.models import F, Sum, Value
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_recursive.fields import RecursiveField

from apps.budget.models import Budget, Function, Agency
from apps.geo.models import Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name', 'slug', 'flag')


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ('id', 'year', 'currency', 'score_open_data', 'score_reports', 'score_data_quality',
                  'transparency_index')


class BudgetAccountSerializer(serializers.ModelSerializer):
    children = serializers.ListSerializer(child=RecursiveField())
    label = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    color_hover = serializers.SerializerMethodField()
    initial_budget_investment = serializers.SerializerMethodField()
    initial_budget_operation = serializers.SerializerMethodField()
    initial_budget_aggregated = serializers.SerializerMethodField()
    budget_investment = serializers.SerializerMethodField()
    budget_operation = serializers.SerializerMethodField()
    budget_aggregated = serializers.SerializerMethodField()
    execution_investment = serializers.SerializerMethodField()
    execution_operation = serializers.SerializerMethodField()
    execution_aggregated = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name', 'initial_budget_investment', 'initial_budget_operation', 'initial_budget_aggregated',
                  'budget_investment', 'budget_operation', 'budget_aggregated',
                  'execution_investment', 'execution_operation', 'execution_aggregated',
                  'last_update', 'children', 'label', 'color', 'color_hover', 'level', 'tree_id')

    def get_initial_budget_investment(self, obj):
        return obj.get_value('initial_budget_investment')

    def get_initial_budget_operation(self, obj):
        return obj.get_value('initial_budget_operation')

    def get_initial_budget_aggregated(self, obj):
        return obj.get_value('initial_budget_aggregated')

    def get_budget_investment(self, obj):
        return obj.get_value('budget_investment')

    def get_budget_operation(self, obj):
        return obj.get_value('budget_operation')

    def get_budget_aggregated(self, obj):
        return obj.get_value('budget_aggregated')

    def get_execution_investment(self, obj):
        return obj.get_value('execution_investment')

    def get_execution_operation(self, obj):
        return obj.get_value('execution_operation')

    def get_execution_aggregated(self, obj):
        return obj.get_value('execution_aggregated')

    def get_label(self, obj):
        return obj.get_taxonomy_label()

    def get_color(self, obj):
        color_index = 0
        execution_value = obj.get_value('execution_aggregated') or 0
        budget_aggregated = obj.get_value('budget_aggregated')

        if not budget_aggregated:
            return settings.TREEMAP_EXECUTION_COLORS[color_index]

        execution_percent = execution_value / budget_aggregated
        if 0.2 < execution_percent <= 0.4:
            color_index = 1
        if 0.4 < execution_percent <= 0.6:
            color_index = 2
        elif 0.6 < execution_percent <= 0.8:
            color_index = 3
        if 0.8 < execution_percent:
            color_index = 4
        return settings.TREEMAP_EXECUTION_COLORS[color_index]

    def get_color_hover(self, obj):
        color = self.get_color(obj)
        return settings.TREEMAP_EXECUTION_COLORS_HOVER[color]


class FunctionSerializer(BudgetAccountSerializer):
    class Meta:
        model = Function
        fields = BudgetAccountSerializer.Meta.fields


class AgencySerializer(BudgetAccountSerializer):
    class Meta:
        model = Agency
        fields = BudgetAccountSerializer.Meta.fields


class HistoricalParamsSerializer(serializers.Serializer):
    budget_account = serializers.ChoiceField(choices=['agencies', 'functions'])
    budget_account_id = serializers.IntegerField(required=False)


class HistoricalDataSerializer(serializers.Serializer):
    year = serializers.CharField()
    budget_aggregated = serializers.FloatField()
    execution_aggregated = serializers.FloatField()


class HistoricalSerializer(serializers.Serializer):
    data = HistoricalDataSerializer()
    name = serializers.CharField()
    id = serializers.IntegerField()


class RankingParamsSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=False)


class RankingSerializer(BudgetSerializer):
    country = CountrySerializer()

    class Meta:
        model = Budget
        fields = BudgetSerializer.Meta.fields + ('country', )


class BudgetViewset(ReadOnlyModelViewSet):
    model = Budget
    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()

    @action(detail=False)
    def ranking(self, request, pk=None):
        """
        Get ranking for budget's transparency_index and it's scores.
        Optional filtered by 'year' (on querystring). If no year is passed, get the latest registered ranking from
        the country.
        :return: {
            'budgets': [RankingSerializer],
            'average': {'score_open_data', 'score_reports', 'score_data_quality', 'transparency_index'}
        }
        """
        params = RankingParamsSerializer(data=request.GET)
        params.is_valid(raise_exception=True)
        filter_year = params.validated_data.get('year', None)

        score_fields = ['score_open_data', 'score_reports', 'score_data_quality', 'transparency_index']

        def get_average_dict(budget_list):
            mean_dict = {}
            for key in score_fields:
                mean_dict[key] = sum(getattr(b, key) for b in budget_list) / len(budget_list)
            return mean_dict

        budget_list = []
        for c in Country.objects.all():
            filters = {'country': c}
            if filter_year:
                filters['year'] = filter_year
            else:
                filters['transparency_index__isnull'] = False
            last_budget_with_index = Budget.objects.select_related('country').filter(**filters).order_by('year').last()
            if last_budget_with_index:
                budget_list.append(last_budget_with_index)

        serializer = RankingSerializer(budget_list, many=True)
        average_dict = get_average_dict(budget_list)
        budgets = sorted(serializer.data, key=lambda i: i['transparency_index'], reverse=True)
        return_data = {'budgets': budgets, 'average': average_dict}
        return Response(return_data)

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

    @action(detail=True)
    def historical(self, request, pk=None):
        budget = self.get_object()
        country = budget.country

        params = HistoricalParamsSerializer(data=request.GET)
        params.is_valid(raise_exception=True)

        budget_account_model = None
        budget_account_param = params.validated_data['budget_account']
        budget_account_id = params.validated_data.get('budget_account_id', None)
        if budget_account_param == 'agencies':
            budget_account_model = Agency
        elif budget_account_param == 'functions':
            budget_account_model = Function
        budget_account_model_name = budget_account_model.get_model_name()  # 'function' or 'agency'

        data = {'code': None, 'name': None, 'data': []}

        if budget_account_id:
            # Get historical data from a specific budget.
            budget_account = budget_account_model.objects.select_related('budget').get(id=budget_account_id)
            code = budget_account.code
            name = budget_account.name
            if not code:
                # If BudgetAccount has no code, get historical data from parent.
                name = budget_account.parent.name
                code = budget_account.parent.code
                if not code:
                    # If parent has no code, return empty list
                    return Response(data)

            qs = budget_account_model.objects.filter(budget__country=country, code=code).values(year=F('budget__year')) \
                .annotate(budget_aggregated=F('budget_aggregated'),
                          execution_aggregated=F('execution_aggregated'),
                          inferred_budget_aggregated=F('inferred_values__budget_aggregated'),
                          inferred_execution_aggregated=F('inferred_values__execution_aggregated')) \
                .order_by('year')
        else:
            # Get aggregated historical data for the country.
            name = country.name
            code = None
            qs = Budget.objects.filter(country=country).values('year') \
                .annotate(budget_aggregated=F(f'{budget_account_model_name}_budget'),
                          execution_aggregated=F(f'{budget_account_model_name}_execution'),
                          inferred_budget_aggregated=F(f'{budget_account_model_name}_budget'),
                          inferred_execution_aggregated=F(f'{budget_account_model_name}_execution')) \
                .order_by('year')

        data_serializer = HistoricalDataSerializer(qs, many=True)

        data['name'] = name
        data['code'] = code
        data['data'] = data_serializer.data
        serializer = HistoricalSerializer(data=data)

        return Response(serializer.initial_data)
