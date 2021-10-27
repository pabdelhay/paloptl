import operator
from functools import reduce

from django.conf import settings
from django.db.models import F, Q
from rest_framework import serializers
from rest_framework.decorators import action
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

class PercentalParamSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=True)
    category = serializers.CharField(required=True)
    #level = serializers.IntegerField(required=True)

class ExpensesByCountryFilterSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=True)

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
            last_transparency_index = TransparencyIndex.objects.select_related('country')\
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

    @action(detail=False)
    def hello(self, request, pk=None):
        despesas = Expense.objects.all();
        return Response(f"Despesas: {despesas}")

        lista = TransparencyIndex.objects.filter(year=2020)
        soma = 0
        for t in lista:
            soma += t.transparency_index

        media = soma / len(lista)
        return Response(f"Media: {media}")

    @action(detail=False)
    def despesa_2020(self, request):
        lista = BudgetSummary.objects.filter(budget__year='2020').values('expense_functional_budget', 'budget__country')
        dic = {}
        for l in lista:
            dic[l['budget__country']] = l['expense_functional_budget']

        return Response(dic)

    @action(detail=False)
    def country_list(self, request):
        return Response("Lista de paises")

    @action(detail=False)
    def expenses_by_country(self, request):
        params = ExpensesByCountryFilterSerializer(data=request.GET)
        params.is_valid(raise_exception=True)
        year = params.validated_data.get('year')

        countries = Country.objects.all()
        result = {
            'categories':[],
            'data':[]
        }

        categories = Category.objects.filter(group="functional", type="expense").values_list("name", flat=True)
        result['categories'] = list(categories)

        for country in countries:

            category_map = CategoryMap.objects.filter(country=country, category__group="functional", category__type="expense")
            name_by_code = {}

            for cm in category_map:
                name_by_code[cm.code] = cm.category.name

            codes = name_by_code.keys()

            result_expense = {
                'country': country.name,

            }
            #inicialize result expense categories None
            for category in categories:
                result_expense[category] = None

            expenses = Expense.objects.filter(budget__country=country, budget__year=year, code__in=codes, group='functional')
            #print(expenses)

            budget = BudgetSummary.objects.filter(budget__year=year, budget__country=country).values('expense_functional_budget').first()

            if not budget:
                result['data'].append(result_expense)
                continue
            budget_country = budget['expense_functional_budget']

            #create the dictionary
            for expense in expenses:
                name_category = name_by_code[expense.code]
                budget_aggregated = expense.budget_aggregated / budget_country if budget_country else None
                result_expense[name_category] = budget_aggregated * 100

            result['data'].append(result_expense)

        return Response(result)
    # @action(detail=False)
    # def expenses_by_country(self, request):
    #     params = ExpensesByCountryFilterSerializer(data=request.GET)
    #     params.is_valid(raise_exception=True)
    #     year = params.validated_data.get('year')
    #     result = []
    #     countries = Country.objects.all()
    #
    #     for country in countries:
    #         dic = {}
    #         filters = {'budget__year': year, 'budget__country': country, 'group': 'functional'}
    #
    #         budget = BudgetSummary.objects.filter(budget__year=year, budget__country=country).values('expense_functional_budget').first()
    #
    #         budget_country = budget['expense_functional_budget']
    #
    #         if not budget_country:
    #             continue
    #
    #         budget_health = Expense.objects.filter(**filters, name__iexact="saúde").values("budget_aggregated").first()
    #         budget_education = Expense.objects.filter(**filters, name__iexact="educação").values("budget_aggregated").first()
    #         budget_security = Expense.objects.filter(**filters, name__iexact="segurança").values("budget_aggregated").first()
    #
    #         dic['country'] = country.name
    #         dic['expense_health'] = budget_health['budget_aggregated'] / budget_country if budget_health else None
    #         dic['expense_education'] = budget_education['budget_aggregated'] / budget_country if budget_education else None
    #         dic['expense_security'] = budget_security['budget_aggregated'] / budget_country if budget_security else None
    #
    #         result.append(dic)
    #
    #     return Response(result)

    @action(detail=False)
    def budget_category_percentage(self, request):
        params = PercentalParamSerializer(data=request.GET)
        params.is_valid(raise_exception=True)
        category = params.validated_data['category']
        year = params.validated_data['year']
        #level = params.validated_data['level']

        orcamento_saude_pais = Expense.objects.filter(budget__year=year, level=0, group="functional", name__iexact=category).values("budget__country", "budget__country__name", "budget_aggregated")
        orcamento_total_pais = BudgetSummary.objects.filter(budget__year="2020").values("expense_functional_budget","budget__country")
        lista_final = []
        dict_orcamento_total = {}

        for i in orcamento_total_pais:
            dict_orcamento_total[i["budget__country"]] = i["expense_functional_budget"]

        for l in orcamento_saude_pais:
            country_id = l["budget__country"]
            orcamento_saude = l["budget_aggregated"]
            if not country_id or not orcamento_saude: continue
            percental = orcamento_saude / dict_orcamento_total[country_id]
            resultado_dict = {"country": l["budget__country__name"], "percental": percental}
            lista_final.append(resultado_dict)

        return Response(lista_final)

    @action(detail= False)
    def RevenueByFunction(self, request):
        revenue = Revenue.objects.all()
        return Response(revenue)

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
