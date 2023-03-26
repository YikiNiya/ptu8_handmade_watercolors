from django import forms
from . import models


class CustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = ['user', 'phone', 'shipping_address']


class OrderForm(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = ['customer_email']
        widgets = {
            'customer_email': forms.HiddenInput(),
        }


class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    country = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    zip_code = forms.CharField(max_length=20)
    shipping_address = forms.CharField(max_length=200)
    phone_number = forms.CharField(max_length=20)
    card_number = forms.CharField(max_length=20)
    payment_method = forms.ChoiceField(choices=[('debit_card', 'Debit card'), ('credit_card', 'Credit Card'), ('paypal', 'PayPal')])
    name_on_card = forms.CharField(max_length=100)
    expiration_date = forms.CharField(max_length=10)
    cvv = forms.CharField(max_length=4)


class CartItemForm(forms.ModelForm):
    class Meta:
        model = models.CartItem
        fields = ['product', 'quantity']


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = models.ProductReview
        fields = ['title', 'body', 'rating']