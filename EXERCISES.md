## 1. Despesas de nível 0 de São Tomé em 2020

## 2. Soma das dotações das despesas acima 

## 3. Pegar (2) pelo BudgetSummary

## 4. Criar um dict neste formato:
    {
        'expense': 10000  # expense_functional_budget,
        'revenue': 20000  # revenue_nature_budget,
    }
    
## 5. Despesas e receitas agregadas de STP para todos os anos, neste formato:
    [
        {
            'year': 2016,
            'expense': 1000,
            'revenue': 2000
        },
        {
            'year': 2017,
            'expense': 1300,
            'revenue': 2400
        },
    ]
   
## 6. Colocar (5) numa api.



# Guiné Bissau

## 1. Todas as despesas organicas de Guiné em 2018

## 2. Somatório de todas as despesas de Guiné em 2018

## 3. Nova página

TUDO dentro do directorio **/frontend/**
 
    1. Criar VIEW em views.py 
    2. Criar TEMPLATE (novo .html)
    3. Criar URL em urls.py
    
## 4. Links para as páginas dos países
    1. Fazer QUERYSET na view 
    2. Fazer FOR no template
    

# Timor Leste

## 1. Declarar um dicionário onde as CHAVES são os nomes dos participantes e os VALORES são sua cidade natal

## 1. [en] Declare a dict where KEYS are the name of participants and VALUES its born city


# Moçambique

## 1. Imprimir slug e currency de todos os países.

## 2. Imprimir os anos que Moçambique tem orçamento.

## 3. Imprimir todas as despesas de função de Moçambique em 2019.

## 4. Porcetagem de execução das desepesas functionais de Moçambique em todos os anos.

2016 - 80%\
2017 - 90%\
2018 - 110%

```
[
    {'year': 2020, 'percent': 80},
    {'year': 2019, 'percent': 80},
    {'year': 2018, 'percent': 80},
]
```

## 5. API que retorne despesas detalhadas por ano de um pais pelo seu código e grupo
eg.: GET /api/myapi/endpoint?country=...&code=...&group=...\
Formato de retorno:
```
[
    {'name': 'Saude', 'year': 2020, 'budget_operation': float, 'budget_investment': float, 'execution_operation': float, 'execution_investment': float},
    {'name': 'Saude', 'year': 2021, 'budget_operation': float, 'budget_investment': float, 'execution_operation': float, 'execution_investment': float},
    {'name': 'Saude', 'year': 2022, 'budget_operation': float, 'budget_investment': float, 'execution_operation': float, 'execution_investment': float},
]
```

## 6. 
-   Criar form (frontend/forms.py)
-   Passar form na view (frontend/student_views/moz_pablo.py)
-   Fazer um bind dos campos do formulario para atualizar o chart (assets/students/moz_pablo.js)
-   Recarregar o chart com a variavel selecionada no form