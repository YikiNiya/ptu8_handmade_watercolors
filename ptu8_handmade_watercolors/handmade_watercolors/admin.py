from django.contrib import admin
from . import models


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'customer', 'date', 'status', 'order_total')
    list_filter = ('status', 'date')
    search_fields = ('customer__user__username', 'product__name')
    

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'subcategory', 'price', 'status', 'stock_level', 'image')
    list_filter = ('category', 'status')
    search_fields = ('name', 'description', 'category__name', 'subcategory__name')
    readonly_fields = ('image',)

    # def image_thumbnail(self, obj):
    #     return format_html('<')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_products')
    search_fields = ('name',)

    def num_products(self, obj):
        return obj.products.count()
    
    num_products.short_description = 'Number of products'


class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category__name')

admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Customer)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Subcategory, SubcategoryAdmin)