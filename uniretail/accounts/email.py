"""
Email utilities for vendor notifications.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_vendor_approval_email(vendor):
    """
    Send approval notification email to a vendor.
    
    Args:
        vendor: CustomUser instance with role='VENDOR'
    """
    subject = "UniRetail: Your Vendor Account Has Been Approved!"
    
    context = {
        'vendor_name': vendor.get_full_name() or vendor.username,
        'vendor_username': vendor.username,
        'dashboard_url': f"{settings.SITE_URL}/dashboard/" if hasattr(settings, 'SITE_URL') else 'https://uniretail.example.com/dashboard/',
    }
    
    # Render the email template
    html_message = render_to_string('emails/vendor_approval.html', context)
    plain_message = render_to_string('emails/vendor_approval.txt', context)
    
    # Send the email
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[vendor.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_vendor_revocation_email(vendor):
    """
    Send revocation notification email to a vendor.
    
    Args:
        vendor: CustomUser instance with role='VENDOR'
    """
    subject = "UniRetail: Your Vendor Account Access Has Been Revoked"
    
    context = {
        'vendor_name': vendor.get_full_name() or vendor.username,
        'vendor_username': vendor.username,
        'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@uniretail.example.com'),
    }
    
    # Render the email template
    html_message = render_to_string('emails/vendor_revocation.html', context)
    plain_message = render_to_string('emails/vendor_revocation.txt', context)
    
    # Send the email
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[vendor.email],
        html_message=html_message,
        fail_silently=False,
    )
