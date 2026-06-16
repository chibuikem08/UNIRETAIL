from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem


class OrderItemInline(admin.TabularInline):
    model  = OrderItem
    extra  = 0
    readonly_fields = ('unit_price', 'subtotal')

    def subtotal(self, obj):
        return f'₦{obj.subtotal}'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('id', 'buyer', 'status', 'total_price', 'item_count', 'created_at')
    list_filter   = ('status',)
    search_fields = ('buyer__username',)
    inlines       = [OrderItemInline]
    readonly_fields = ('total_price', 'created_at', 'updated_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'total', 'updated_at')
