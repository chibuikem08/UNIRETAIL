from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .email import send_vendor_approval_email, send_vendor_revocation_email


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
        """Bulk action to approve vendors and send approval emails."""
        vendors = queryset.filter(role='VENDOR', is_approved_vendor=False)
        updated = vendors.update(is_approved_vendor=True)
        
        # Send approval emails to each vendor
        successful_emails = 0
        failed_emails = 0
        
        for vendor in vendors:
            try:
                send_vendor_approval_email(vendor)
                successful_emails += 1
            except Exception as e:
                failed_emails += 1
                print(f"Failed to send email to {vendor.email}: {str(e)}")
        
        message = f'{updated} vendor(s) approved.'
        if successful_emails > 0:
            message += f' {successful_emails} approval email(s) sent.'
        if failed_emails > 0:
            message += f' {failed_emails} email(s) failed to send.'
        
        self.message_user(request, message)
    approve_vendors.short_description = 'Approve selected vendors and send approval emails'

    def revoke_vendor_approval(self, request, queryset):
        """Bulk action to revoke vendor approval and send revocation emails."""
        vendors = queryset.filter(role='VENDOR', is_approved_vendor=True)
        updated = vendors.update(is_approved_vendor=False)
        
        # Send revocation emails to each vendor
        successful_emails = 0
        failed_emails = 0
        
        for vendor in vendors:
            try:
                send_vendor_revocation_email(vendor)
                successful_emails += 1
            except Exception as e:
                failed_emails += 1
                print(f"Failed to send email to {vendor.email}: {str(e)}")
        
        message = f'{updated} vendor approval(s) revoked.'
        if successful_emails > 0:
            message += f' {successful_emails} revocation email(s) sent.'
        if failed_emails > 0:
            message += f' {failed_emails} email(s) failed to send.'
        
        self.message_user(request, message)
    revoke_vendor_approval.short_description = 'Revoke vendor approval and send revocation emails'
