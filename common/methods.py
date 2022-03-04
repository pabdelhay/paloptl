from django.conf import settings
from djmoney.money import Money
import requests


def money_display(amount, currency):
    return str(Money(amount, currency))


def raw_money_display(amount):
    return Money(amount, settings.RAW_CURRENCY)



