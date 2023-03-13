from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=250, default='', blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='products', null=True, blank=True)
    stock_level = models.IntegerField(default=0)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey('Subcategory', on_delete=models.CASCADE, related_name='products', null=True, default=None)

    def __str__(self):
        return self.name
    

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shipping_address = models.TextField()

    def __str__(self):
        return self.user.username


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    customer_email = models.EmailField()
    order_total= models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f'Order {self.id}'    


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self):
        return self.name