from django import template
from django.conf import settings

register = template.Library()

# Tasas de cambio (simplificadas para este ejemplo)
EXCHANGE_RATES = {
    'CLP': 1.0,
    'USD': 0.0012,  # 1 CLP = 0.0012 USD
    'EUR': 0.0010,  # 1 CLP = 0.0010 EUR
}

@register.filter
def convert_currency(price, currency='CLP'):
    """
    Convierte un precio de CLP a la divisa especificada
    """
    if not price:
        return 0
    
    try:
        price = float(price)
        rate = EXCHANGE_RATES.get(currency, 1.0)
        converted_price = price * rate
        
        # Formatear según la divisa
        if currency == 'CLP':
            return f"${int(converted_price):,}".replace(',', '.')
        elif currency == 'USD':
            return f"US${converted_price:.2f}"
        elif currency == 'EUR':
            return f"€{converted_price:.2f}"
        else:
            return f"{converted_price:.2f} {currency}"
    except (ValueError, TypeError):
        return price