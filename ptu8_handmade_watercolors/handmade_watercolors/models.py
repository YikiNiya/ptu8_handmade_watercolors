from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from tinymce.models import HTMLField

User = get_user_model()


class Product(models.Model):
    STATUS_CHOICE = (
        ('available', 'Available'),
        ('out_of_stock', 'Out of stock'),
        ('coming_soon', 'Coming soon'),
        ('discontinued', 'Discontinued'),
        ('on_sale', 'On sale'),        
    )

    name = models.CharField(max_length=255)
    description = HTMLField(max_length=250, default='', blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image_url = models.CharField(max_length=400, null=True, blank=True)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    stock_level = models.IntegerField(default=0)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey('Subcategory', on_delete=models.CASCADE, related_name='products', null=True, default=None)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='available')
    
    def __str__(self):
        return self.name
    

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    phone = models.CharField(max_length=15, default='')
    shipping_address = models.TextField()

    def __str__(self):
        return self.user.username


class Order(models.Model):
    ORDER_STATUS_CHOICE = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    )

    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    email = models.EmailField()
    country = models.CharField(max_length=100, default='')
    city = models.CharField(max_length=100, default='')
    zip_code = models.CharField(max_length=20, default='')
    shipping_address = models.CharField(max_length=200, default='')
    phone_number = models.CharField(max_length=20, default='')
    card_number = models.CharField(max_length=20, default='0000-0000-0000-0000')
    PAYMENT_CHOICE = (
        ('debit_card', 'Debit card'),
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
    )

    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICE, default='debit_card')
    name_on_card = models.CharField(max_length=100,  default='')
    expiration_date = models.CharField(max_length=10, default='')
    cvv = models.CharField(max_length=4, default='')
    date = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_total = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICE, default='pending')

    def __str__(self):
        return f'Order {self.id}'    
    
    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order.objects.filter(customer=customer_id).order_by('-date') 


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        return self.quantity * self.price


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    cart_total = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s cart"


class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class ProductReview(models.Model):
    RATING_CHOICES = (
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐')
    )

    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=255)
    body = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES, default='')

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'