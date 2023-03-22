from django import template

register = template.Library()

@register.filter
def get_cart_items(product, cart):
    keys = cart.keys ()
    for id in keys:
        if int (id) == product.id:
            return True
    return False

@register.filter
def total(cart_items):
    return sum(item.product.price * item.quantity for item in cart_items)

@register.filter (name='total_cart_price')
def total_cart_price(products, cart):
    sum = 0
    for p in products:
        sum += total (p, cart)
    return sum