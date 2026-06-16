from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username', 'email', 'role', 'is_approved_vendor', 'is_active', 'date_joined')
    list_filter   = ('role', 'is_approved_vendor', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering      = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('UniRetail Info', {
            'fields': ('role', 'phone_number', 'profile_picture', 'is_approved_vendor')
        }),
    )

    actions = ['approve_vendors', 'revoke_vendor_approval']

    def approve_vendors(self, request, queryset):
        updated = queryset.filter(role='VENDOR').update(is_approved_vendor=True)
        self.message_user(request, f'{updated} vendor(s) approved.')
    approve_vendors.short_description = 'Approve selected vendors'

    def revoke_vendor_approval(self, request, queryset):
        updated = queryset.filter(role='VENDOR').update(is_approved_vendor=False)
        self.message_user(request, f'{updated} vendor approval(s) revoked.')
    revoke_vendor_approval.short_description = 'Revoke vendor approval'
