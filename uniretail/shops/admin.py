from django.contrib import admin
from .models import Shop, Product


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display  = ('name', 'vendor', 'category', 'is_open', 'product_count', 'created_at')
    list_filter   = ('category', 'is_open')
    search_fields = ('name', 'vendor__username')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ('name', 'shop', 'category', 'price', 'stock', 'is_available')
    list_filter   = ('category', 'is_available', 'shop')
    search_fields = ('name', 'shop__name')
    prepopulated_fields = {'slug': ('name',)}
