import requests
from django.conf import settings
from djmoney.money import Money
from config.settings import FREECURRENCY_ACCESS_KEY


def money_display(amount, currency):
    return str(Money(amount, currency))


def raw_money_display(amount):
    return Money(amount, settings.RAW_CURRENCY)


def get_rates(base_currency):
    url = f"https://freecurrencyapi.net/api/v2/latest?apikey={FREECURRENCY_ACCESS_KEY}&base_currency={base_currency}"
    r = requests.get(url)
    result = r.json()
    return result.get('data')
