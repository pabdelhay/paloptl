import requests
from django.conf import settings
from djmoney.money import Money


def money_display(amount, currency):
    return str(Money(amount, currency))


def raw_money_display(amount):
    return Money(amount, settings.RAW_CURRENCY)


def apply_exchange(amount, currency, dic):
    url = f"https://freecurrencyapi.net/api/v2/latest?apikey={settings.CURRENCY_KEY}&base_currency=EUR"
    get_res_url = requests.get(url)
    results = get_res_url.json()

    rates = results["data"]

    rate = rates[currency]
    dic["rate"] = rate

    return amount / rate


def exchange_base_currency(base_currency):
    url = f"https://freecurrencyapi.net/api/v2/latest?apikey={settings.CURRENCY_KEY}&base_currency={base_currency}"

    get_res_url = requests.get(url)
    results = get_res_url.json()

    rates = results["data"]

    return rates


def calculator_exchange(amount, currency, dic, rates, base_currency):
    if currency != base_currency:
        rate = rates[currency]
        dic["rate"] = rate


    else:
        dic["rate"] = 1
        rate = 1

    return amount / rate


def palop_calculator_exchange(amount, currency, rates, base_currency):
    if currency != base_currency:
        rate = rates[currency]
        return amount / rate

    else:
        return amount


def data_year_budget(data, dic_country_budget, rates, base_currency):
    total_budget_year = 0

    for db in data:

        func = db.expense_functional_budget
        orga = db.expense_organic_budget
        currency = db.budget.currency

        if func is not None:
            amount_in_base_currency = palop_calculator_exchange(func, currency, rates, base_currency)
            dic_country_budget[db.budget.country.name] = amount_in_base_currency
            total_budget_year = total_budget_year + amount_in_base_currency

        else:
            if orga is not None:
                amount_in_base_currency = palop_calculator_exchange(orga, currency, rates, base_currency)
                dic_country_budget[db.budget.country.name] = amount_in_base_currency
                total_budget_year = total_budget_year + amount_in_base_currency

    return total_budget_year
