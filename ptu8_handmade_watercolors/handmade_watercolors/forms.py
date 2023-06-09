from django import forms
from . import models


class CustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = ['user', 'phone', 'shipping_address']


class OrderForm(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = ['email']
        widgets = {
            'email': forms.HiddenInput(),
        }


class CartItemForm(forms.ModelForm):
    class Meta:
        model = models.CartItem
        fields = ['product', 'quantity']


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = models.ProductReview
        fields = ['title', 'body', 'rating']