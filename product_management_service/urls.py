"""
URL configuration for the product management service.

This module defines the URL patterns for product and category
resources, mapping them to their respective views.
"""

from django.urls import path
from .views import ProductList, ProductDetail, CategoryList, CategoryDetail

urlpatterns = [
    path('products', ProductList.as_view(), name='product-list'),
    path('products/<int:pk>', ProductDetail.as_view(), name='product-detail'),
    path('categories', CategoryList.as_view(), name='category-list'),
    path('categories/<int:pk>', CategoryDetail.as_view(), name='category-detail'),
]
