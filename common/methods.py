from django.conf import settings
from djmoney.money import Money
import requests


def money_display(amount, currency):
    return str(Money(amount, currency))


def raw_money_display(amount):
    return Money(amount, settings.RAW_CURRENCY)

def apply_exchange(base_currency):
    api_key = settings.FIXED_ACESS_KEY_CURRENCY_CHANGE
    url = f"https://freecurrencyapi.net/api/v2/latest?apikey={api_key}&base_currency={base_currency}"
    r = requests.get(url)
    result = r.json()
    
    return result['data']


