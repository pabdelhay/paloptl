import operator
from functools import reduce

from django.conf import settings
from django.db.models import F, Q
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.budget.choices import ExpenseGroupChoices, RevenueGroupChoices
from apps.budget.models import Budget, TransparencyIndex, Expense, Revenue, BudgetSummary, Category, CategoryMap
from apps.geo.models import Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name', 'slug', 'flag')


class BudgetSerializer(serializers.ModelSerializer):
    currency_display = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = ('id', 'year', 'currency', 'currency_display', 'output_file')

    def get_currency_display(self, obj):
        return obj.get_currency_display()


class BudgetAccountSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
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
    execution_percentage = serializers.SerializerMethodField()
    has_budget = serializers.SerializerMethodField()

    def __init__(self, instance, no_children=False, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        if no_children:
            self.fields.pop('children')

    class Meta:
        fields = ('id', 'name', 'initial_budget_investment', 'initial_budget_operation', 'initial_budget_aggregated',
                  'budget_investment', 'budget_operation', 'budget_aggregated',
                  'execution_investment', 'execution_operation', 'execution_aggregated', 'execution_percentage',
                  'last_update', 'children', 'color', 'color_hover', 'parent_id', 'level', 'tree_id', 'has_budget')

    def get_children(self, obj):
        if obj.level == 1:
            # For level 1, we return children as itself.
            return [self.__class__(instance=obj, no_children=True).data]
        qs = obj.get_descendants(include_self=False).order_by('-budget_aggregated')
        return self.__class__(instance=qs, many=True).data

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
        # If no budget, send execution as the budget.
        return obj.get_value('budget_aggregated') or obj.get_value('execution_aggregated')

    def get_execution_investment(self, obj):
        return obj.get_value('execution_investment')

    def get_execution_operation(self, obj):
        return obj.get_value('execution_operation')

    def get_execution_aggregated(self, obj):
        return obj.get_value('execution_aggregated')

    def get_execution_percentage(self, obj):
        budget_aggregated = obj.get_value('budget_aggregated')
        execution_aggregated = obj.get_value('execution_aggregated')
        if not budget_aggregated or not execution_aggregated:
            return None
        return execution_aggregated / budget_aggregated

    def get_color(self, obj):
        color_index = 0
        execution_value = obj.get_value('execution_aggregated') or 0
        budget_aggregated = obj.get_value('budget_aggregated')

        if not budget_aggregated or not execution_value:
            return settings.TREEMAP_EXECUTION_COLORS[color_index]

        execution_percent = execution_value / budget_aggregated
        if execution_percent <= 0.2:
            color_index = 1
        elif 0.2 < execution_percent <= 0.4:
            color_index = 2
        elif 0.4 < execution_percent <= 0.6:
            color_index = 3
        elif 0.6 < execution_percent <= 0.8:
            color_index = 4
        elif 0.8 < execution_percent:
            color_index = 5
        return settings.TREEMAP_EXECUTION_COLORS[color_index]

    def get_color_hover(self, obj):
        color = self.get_color(obj)
        return settings.TREEMAP_EXECUTION_COLORS_HOVER[color]

    def get_has_budget(self, obj):
        return True if obj.get_value('budget_aggregated') else False


class BudgetAccountLeafSerializer(BudgetAccountSerializer):
    class Meta:
        fields = ('id', 'name', 'initial_budget_investment', 'initial_budget_operation', 'initial_budget_aggregated',
                  'budget_investment', 'budget_operation', 'budget_aggregated',
                  'execution_investment', 'execution_operation', 'execution_aggregated', 'execution_percentage',
                  'last_update', 'color', 'color_hover', 'parent_id', 'level', 'tree_id')


class BudgetAccountFilterSerializer(serializers.Serializer):
    group = serializers.CharField(max_length=30)


class ExpenseSerializer(BudgetAccountSerializer):
    class Meta:
        model = Expense
        fields = BudgetAccountSerializer.Meta.fields


class RevenueSerializer(BudgetAccountSerializer):
    class Meta:
        model = Revenue
        fields = BudgetAccountSerializer.Meta.fields


class HistoricalParamsSerializer(serializers.Serializer):
    group = serializers.ChoiceField(choices=ExpenseGroupChoices.choices + RevenueGroupChoices.choices)
    budget_account = serializers.ChoiceField(choices=['expenses', 'revenues'])
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


class RankingSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = TransparencyIndex
        fields = ('id', 'country', 'year', 'score_open_data', 'score_reports', 'score_data_quality',
                  'transparency_index',)


class ExpensePerYearCategoryFilterSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    category = serializers.CharField(max_length=100)


class ExpensePerYearFilterSerializer(serializers.Serializer):
    year = serializers.IntegerField()


class CountryFilterSerializer(serializers.Serializer):
    # country = serializers.IntegerField()
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())


class BudgetsPerYearSerializer(serializers.Serializer):
    # country = serializers.IntegerField()

    year = serializers.IntegerField()
    budget_expense = serializers.FloatField()
    budget_revenue = serializers.FloatField()
    budget_expense_group = serializers.CharField()
    budget_revenue_group = serializers.CharField()

    execution_revenue = serializers.FloatField()
    execution_expense = serializers.FloatField()


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
            last_transparency_index = TransparencyIndex.objects.select_related('country') \
                .filter(**filters).order_by('year').last()
            if last_transparency_index:
                budget_list.append(last_transparency_index)

        serializer = RankingSerializer(budget_list, many=True)
        average_dict = get_average_dict(budget_list)
        budgets = sorted(serializer.data, key=lambda i: i['transparency_index'], reverse=True)
        return_data = {'budgets': budgets, 'average': average_dict}
        return Response(return_data)

    @action(detail=True)
    def expenses(self, request, pk=None):
        budget = self.get_object()
        params = BudgetAccountFilterSerializer(data=request.GET)
        params.is_valid(raise_exception=True)
        group = params.validated_data.get('group')

        qs = Expense.objects.filter(budget=budget, level=0, group=group) \
            .exclude(Q(budget_aggregated__isnull=True) & Q(execution_aggregated__isnull=True))
        serializer = ExpenseSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def revenues(self, request, pk=None):
        budget = self.get_object()
        params = BudgetAccountFilterSerializer(data=request.GET)
        params.is_valid(raise_exception=True)
        group = params.validated_data.get('group')

        qs = Revenue.objects.filter(budget=budget, level=0, group=group) \
            .exclude(Q(budget_aggregated__isnull=True) & Q(execution_aggregated__isnull=True))
        serializer = ExpenseSerializer(qs, many=True)
        return Response(serializer.data)


    @action(detail=True)
    def historical(self, request, pk=None):
        budget = self.get_object()
        country = budget.country

        params = HistoricalParamsSerializer(data=request.GET)
        params.is_valid(raise_exception=True)

        budget_account_model = None
        group = params.validated_data['group']
        budget_account_param = params.validated_data['budget_account']
        budget_account_id = params.validated_data.get('budget_account_id', None)
        if budget_account_param == 'expenses':
            budget_account_model = Expense
        elif budget_account_param == 'revenues':
            budget_account_model = Revenue
        budget_account_model_name = budget_account_model.get_model_name()  # 'expense' or 'revenue'

        data = {'code': None, 'name': None, 'data': []}

        if budget_account_id:
            # Get historical data from a specific budget.
            budget_account = budget_account_model.objects.select_related('budget').get(id=budget_account_id)
            code = budget_account.code
            name = budget_account.name
            parent = budget_account.parent

            ba_filters = {
                'budget__country': country,
                'group': group,
                'level': budget_account.level
            }
            filter_name_code = [Q(name__iexact=name)]
            if code:
                filter_name_code.append(Q(code=code))

            qs = budget_account_model.objects.filter(**ba_filters).filter(reduce(operator.or_, filter_name_code))
            if parent:
                filter_parent = [Q(parent__name__iexact=parent.name)]
                if parent.code:
                    filter_parent.append(Q(parent__code__iexact=parent.code))
                qs = qs.filter(reduce(operator.or_, filter_parent))
            qs = qs.values(year=F('budget__year')) \
                .annotate(budget_aggregated=F('budget_aggregated'),
                          execution_aggregated=F('execution_aggregated'),
                          inferred_budget_aggregated=F('inferred_values__budget_aggregated'),
                          inferred_execution_aggregated=F('inferred_values__execution_aggregated')) \
                .order_by('year')
        else:
            # Get aggregated historical data for the country.
            name = country.name
            code = None
            qs = BudgetSummary.objects.filter(budget__country=country).values(year=F('budget__year')) \
                .annotate(budget_aggregated=F(f'{budget_account_model_name}_{group}_budget'),
                          execution_aggregated=F(f'{budget_account_model_name}_{group}_execution'),
                          inferred_budget_aggregated=F(f'{budget_account_model_name}_{group}_budget'),
                          inferred_execution_aggregated=F(f'{budget_account_model_name}_{group}_execution')) \
                .order_by('year')

        data_serializer = HistoricalDataSerializer(qs, many=True)

        data['name'] = name
        data['code'] = code
        data['data'] = data_serializer.data
        serializer = HistoricalSerializer(data=data)

        return Response(serializer.initial_data)

    @action(detail=False)
    def teste(self, request, pk=None):
        return Response("ola teste")

    @action(detail=False)
    def budget_expense_revenue(self, request, pk=None):

        params = CountryFilterSerializer(data=request.GET)
        params.is_valid(raise_exception=True)
        country = params.validated_data.get('country')
        budget_stp = Budget.objects.filter(country=country).order_by('year')
        budget_list = list()

        for i in budget_stp:
            j = BudgetSummary.objects.get(budget=i)
            budget_expense_flag = "functional"
            budget_expense_value = j.expense_functional_budget
            if not j.expense_functional_budget:
                budget_expense_value = j.expense_organic_budget
                budget_expense_flag = "organic"

            budget_revenue_flag = "nature"
            budget_revenue_value = j.revenue_nature_budget
            if not j.revenue_nature_budget:
                budget_revenue_value = j.revenue_source_budget
                budget_revenue_flag = "source"

            budget_list.append(
                {
                    'year': j.budget.year,
                    'budget_expense': budget_expense_value,
                    'budget_expense_group': budget_expense_flag,
                    'budget_revenue': budget_revenue_value,
                    'budget_revenue_group': budget_revenue_flag,
                    'execution_revenue': j.revenue_nature_execution,
                    'execution_expense': j.expense_functional_execution
                }
            )

        budget_list_s = BudgetsPerYearSerializer(budget_list, many=True)

        return Response(budget_list_s.data)

    @action(detail=False)
    def budget_category_percentage(self, request, pk=None):
        """
            Get all Expenses by category and calculate percentage
        """
        params = ExpensePerYearCategoryFilterSerializer(data=request.GET)
        params.is_valid(raise_exception=True)
        year = params.validated_data.get('year')
        category = params.validated_data.get('category')
        budgetSummarys = BudgetSummary.objects.filter(budget__year=year).values('expense_functional_budget', 'budget__country__id')
        dbudgetSummary = {}
        for budgetSummary in budgetSummarys:
            dbudgetSummary[budgetSummary['budget__country__id']] = budgetSummary['expense_functional_budget']

        expenses = Expense.objects.filter(
            budget__year=year, group='functional', name__iexact=category
        ).values('budget_aggregated', 'budget__country__name', 'budget__country')

        agregateExpenses = []
        for expense in expenses:
            if expense['budget_aggregated'] is not None:
                agregateExpense = {}
                totalbudgetSummaryCountry = dbudgetSummary[expense['budget__country']]
                agregateExpense['country'] = expense['budget__country__name']
                agregateExpense['percent'] = (expense['budget_aggregated'] / totalbudgetSummaryCountry) * 100;
                agregateExpenses.append(agregateExpense)
        return Response(agregateExpenses)

    @action(detail=False)
    def expense_by_country(self, request, pk=None):
        """
            Get Expenses by category and calculate percentage
        """
        params = ExpensePerYearFilterSerializer(data=request.GET)
        params.is_valid(raise_exception=True)
        year = params.validated_data.get('year')

        budgetSummarys = BudgetSummary.objects.filter(
            budget__year=year
        ).values('expense_functional_budget', 'budget__country__id')

        dbudgetSummary = {}
        for budgetSummary in budgetSummarys:
            dbudgetSummary[budgetSummary['budget__country__id']] = budgetSummary['expense_functional_budget']

        categories_qs = Category.objects.all()
        categories = []
        for category in categories_qs:
            categories.append(category.name)

        agregateExpenses = []
        countries = Country.objects.all()
        for country in countries:
            categoriesMaps = CategoryMap.objects.filter(
                country=country, category__group='functional',
                category__type='expense'
            ).select_related('category')

            aggregateExpense = {"country": country.name}
            categoriesnames = {}
            for categoryMap in categoriesMaps:
                categoriesnames[categoryMap.code] = categoryMap.category.name
                aggregateExpense[categoryMap.category.name] = None

            if len(categoriesnames) > 0:
                categoriesmapscodes = categoriesnames.keys()
                expenses = Expense.objects.filter(
                    budget__country=country, budget__year=year, code__in=categoriesmapscodes,
                    group='functional', level=0
                )

                for expense in expenses:
                    totalbudgetSummaryCountry = dbudgetSummary[country.id]

                    catname = categoriesnames[expense.code]

                    if expense.budget_aggregated and totalbudgetSummaryCountry:
                        expenses_category = expense.budget_aggregated
                        expenses_category_percent = (expenses_category / totalbudgetSummaryCountry) * 100
                        aggregateExpense[catname] = expenses_category_percent
                    else:
                        aggregateExpense[catname] = None

                agregateExpenses.append(aggregateExpense)

        return Response({
            "category": categories,
            "data": agregateExpenses
        })
