from django import template

register = template.Library()

@register.filter
def total(cart_items):
    return sum(item.product.price * item.quantity for item in cart_items)