from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/search/', views.ProductListView.product_list, name='product_search'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('subcategories/', views.SubcategoryListView.as_view(), name='subcategory_list'),
]
