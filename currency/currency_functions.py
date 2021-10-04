from forex_python.converter import CurrencyRates

def convert_to_rouble(value: float, currency: str):
    if currency == "SUR":
        return value
    else:
        c = CurrencyRates()
        return value * c.get_rate(currency, "RUB")