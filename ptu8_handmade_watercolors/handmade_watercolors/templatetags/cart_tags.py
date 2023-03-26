from django import template
from django.conf import settings

register = template.Library()

@register.filter
def get_cart_total_price(cart):
    total = 0
    for item in cart:
        total += item['price'] * item['quantity']
    return total

@register.simple_tag(takes_context=True)
def get_cart_items(context):
    request = context['request']
    cart = request.session.get('cart', {})
    cart_items = []
    for _, item in cart.items():
        product_data = item['product']
        cart_items.append({'product': product_data, 'quantity': item['quantity']})
    return cart_items

@register.filter
def total(cart_items):
    return sum(item.product.price * item.quantity for item in cart_items)

@register.filter(name='currency')
def currency(number):
    return "€ "+str(number)



@register.filter(name='multiply')
def multiply(number , number1):
    return number * number1