from django.contrib import admin
from .models import Category, Product

# Register your models here.

# Category Admin


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category', 'description',
                    'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('parent_category',)
    ordering = ('name',)

# Product Admin


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'stock_quantity',
                    'category', 'barcode', 'created_at', 'updated_at')
    search_fields = ('name', 'sku', 'barcode')
    list_filter = ('category',)
    ordering = ('name', 'sku')
    # Adding filters for price and stock quantity can be helpful for management
    list_filter = ('price', 'stock_quantity', 'category')

# Register models with the admin site


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
