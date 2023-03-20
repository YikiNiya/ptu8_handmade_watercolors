from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/search/', views.ProductListView.product_list, name='product_search'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add_review/<int:pk>/', views.add_review, name='add_review'),  
    path('cart/', views.cart, name='cart'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('subcategories/', views.SubcategoryListView.as_view(), name='subcategory_list'),
]
