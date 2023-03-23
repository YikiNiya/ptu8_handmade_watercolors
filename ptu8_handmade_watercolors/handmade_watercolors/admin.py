from django.contrib import admin
from . import models


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'customer', 'date', 'status', 'order_total')
    list_filter = ('status', 'date')
    search_fields = ('customer__user__username', 'product__name')
    

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'order', 'product', 'quantity', 'price')
    list_filter = ('order', 'product')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_url', 'category', 'subcategory', 'price', 'status', 'stock_level')
    list_filter = ('category', 'status')
    search_fields = ('name', 'description', 'category__name', 'subcategory__name')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_products')
    search_fields = ('name',)

    def num_products(self, obj):
        return obj.products.count()
    
    num_products.short_description = 'Number of products'


class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category__name')


class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'user', 'date', 'rating')
    list_filter = ('product', 'rating', 'date')
    search_fields = ('title', 'body', 'user__username', 'product__name')
    ordering = ('-date',)
    fieldsets = (
        (None, {'fields': ('product', 'user')}),
        ('Review Info', {'fields': ('title', 'body', 'rating')}),
    )


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity')
    list_filter = ('user', 'product')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('id',)


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
    list_filter = ('cart', 'product')
    search_fields = ('product__name',)
    readonly_fields = ('id',)


admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Customer)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.OrderItem, OrderItemAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Subcategory, SubcategoryAdmin)
admin.site.register(models.ProductReview, ProductReviewAdmin)
admin.site.register(models.Cart, CartAdmin)
admin.site.register(models.CartItem, CartItemAdmin)