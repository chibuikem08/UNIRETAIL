from django.contrib import admin
from .models import Payment, VendorBankAccount


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display   = ('reference', 'buyer', 'order', 'amount', 'status', 'paid_at', 'created_at')
    list_filter    = ('status',)
    search_fields  = ('reference', 'buyer__username')
    readonly_fields = ('reference', 'amount', 'paid_at', 'created_at')


@admin.register(VendorBankAccount)
class VendorBankAccountAdmin(admin.ModelAdmin):
    list_display  = ('vendor', 'bank_name', 'account_number', 'account_name', 'is_verified', 'subaccount_code')
    list_filter   = ('is_verified', 'bank_name')
    search_fields = ('vendor__username', 'account_number')
    readonly_fields = ('subaccount_code', 'subaccount_id', 'created_at')
