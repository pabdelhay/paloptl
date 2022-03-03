from django.conf import settings
from djmoney.money import Money
import requests


def money_display(amount, currency):
    return str(Money(amount, currency))


def raw_money_display(amount):
    return Money(amount, settings.RAW_CURRENCY)

def apply_change_euro(amount, currency):
    api_key = settings.FIXED_ACESS_KEY_CURRENCY_CHANGE
    url = f"http://data.fixer.io/api/latest?access_key={api_key}&symbols=USD,AOA,CVE,XOF,MZN,STD&format=1"
    r = requests.get(url)
    result = r.json()
    
    rate = result['rates'].get(currency)

    return amount / rate


def apply_change(base_currency):
    api_key = settings.FIXED_ACESS_KEY_CURRENCY_CHANGE
    url = f"https://freecurrencyapi.net/api/v2/latest?apikey=b9b4ceb0-9634-11ec-ac62-af9b6e9fcc16&base_currency={base_currency}"
    r = requests.get(url)
    result = r.json()
    
    return result['data']


