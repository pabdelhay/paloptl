import requests
from django.conf import settings


def apply_exchange(base_currency):
    api_key = settings.FIXED_ACESS_KEY_CURRENCY_CHANGE
    url = f"https://freecurrencyapi.net/api/v2/latest?apikey={api_key}&base_currency={base_currency}"
    r = requests.get(url)
    result = r.json()

    return result['data']