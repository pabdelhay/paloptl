from djmoney.money import Money


def money_display(amount, currency):
    return str(Money(amount, currency))
