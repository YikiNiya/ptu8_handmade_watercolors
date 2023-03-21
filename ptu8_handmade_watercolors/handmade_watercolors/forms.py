from django import forms
from . import models


class CustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = ['phone', 'shipping_address']


class OrderForm(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = ['quantity', 'customer_email']


class CartItemForm(forms.ModelForm):
    class Meta:
        model = models.CartItem
        fields = ['quantity']


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = models.ProductReview
        fields = ['title', 'body', 'rating']