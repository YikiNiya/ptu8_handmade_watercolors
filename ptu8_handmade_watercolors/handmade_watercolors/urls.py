from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('orders/', views.OrderView.as_view(), name='orders'),
    path('orders/create/', views.OrderCreateView.as_view(), name='orders'),
    path('empty_cart/', views.empty_cart, name='empty_cart'),
    path('products/search/', views.ProductListView.product_list, name='product_search'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('add_review/<int:product_id>/', views.add_review, name='add_review'),  
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('subcategories/', views.SubcategoryListView.as_view(), name='subcategory_list'),
]
