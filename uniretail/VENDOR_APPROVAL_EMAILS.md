# Vendor Approval Email Notifications

## Implementation Summary

A complete email notification system has been implemented for vendor account approvals and revocations in UniRetail. Vendors are now automatically notified when their accounts are approved or revoked.

## Files Created

1. **accounts/email.py** - Email utility functions
   - `send_vendor_approval_email(vendor)` - Sends approval notification
   - `send_vendor_revocation_email(vendor)` - Sends revocation notification

2. **templates/emails/vendor_approval.html** - HTML email template for approvals
3. **templates/emails/vendor_approval.txt** - Plain text version for approvals
4. **templates/emails/vendor_revocation.html** - HTML email template for revocations
5. **templates/emails/vendor_revocation.txt** - Plain text version for revocations

## Files Modified

1. **uniretail/settings.py**
   - Added EMAIL_BACKEND configuration
   - Added email settings for SMTP configuration
   - Added DEFAULT_FROM_EMAIL setting
   - Added SITE_URL for email links
   - Added SUPPORT_EMAIL for support contact in emails

2. **dashboard/views.py**
   - Updated `approve_vendor()` to send approval emails
   - Updated `revoke_vendor()` to send revocation emails
   - Added error handling with user feedback

3. **accounts/admin.py**
   - Updated `approve_vendors()` bulk action to send emails
   - Updated `revoke_vendor_approval()` bulk action to send emails
   - Enhanced action descriptions
   - Added email success/failure tracking

## Features

### Approval Notifications
When an admin approves a vendor through either:
- **Dashboard**: Clicking "Approve" on the admin dashboard (`/dashboard/`)
- **Django Admin**: Using the bulk "Approve selected vendors" action

The vendor receives an email with:
- Confirmation of approval
- Next steps for setting up their shop
- Link to their vendor dashboard
- Professional HTML and plain text formatting

### Revocation Notifications
When an admin revokes vendor approval, the vendor receives an email with:
- Notice of revocation
- Explanation of consequences
- Contact information for support

## Environment Variables

Add these to your `.env` file:

### Development (Console Output)
```
DEBUG=True
```
Emails will be printed to the console instead of sent.

### Production (SMTP Configuration)
```
DEBUG=False
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
SITE_URL=https://yourdomain.com
SUPPORT_EMAIL=support@yourdomain.com
```

## Email Configuration

### For Gmail (Recommended)
1. Enable 2-factor authentication on your Gmail account
2. Generate an "App Password" at https://myaccount.google.com/apppasswords
3. Use the app password in EMAIL_HOST_PASSWORD (not your regular password)

### For Other SMTP Providers
Configure EMAIL_HOST, EMAIL_PORT, and credentials accordingly.

## Error Handling

- **Dashboard approval**: If email sending fails, admin is notified but vendor approval is still processed
- **Admin bulk actions**: Individual email failures are tracked and reported
- **Console backend (dev)**: Emails appear in console output
- **Email failures don't block approvals** - The most important action (marking vendor as approved) succeeds even if notification fails

## Testing

### Local Development
1. Set DEBUG=True in your .env
2. Run Django: `python manage.py runserver`
3. Approve a vendor through dashboard or admin
4. Check the console for email output

### With Console Backend
Emails will be displayed in the terminal where Django is running.

### With Real SMTP
1. Configure SMTP credentials in .env
2. Test by sending approval to a real email address
3. Check that HTML formatting renders correctly in email client

## Customization

### Email Templates
Edit templates in `templates/emails/`:
- `vendor_approval.html` - Modify styling and content
- `vendor_revocation.html` - Modify styling and content

### Email Subject Lines
Edit subjects in `accounts/email.py`:
- `send_vendor_approval_email()` function
- `send_vendor_revocation_email()` function

### Email Context Variables
Available in templates:
- `{{ vendor_name }}` - Full name or username
- `{{ vendor_username }}` - Username
- `{{ dashboard_url }}` - Link to vendor dashboard
- `{{ support_email }}` - Support email address

## Verification Checklist

- [x] Approval emails sent when admin clicks "Approve" on dashboard
- [x] Approval emails sent via Django admin bulk action
- [x] Revocation emails sent when access is revoked
- [x] Email templates created (HTML and plain text)
- [x] Email configuration in settings.py
- [x] Error handling and user feedback
- [x] Development mode (console backend)
- [x] Production mode (SMTP support)

## Integration Points

The email notifications integrate with:
- `CustomUser.is_approved_vendor` field change
- `dashboard/views.py` - approve_vendor() and revoke_vendor() views
- `accounts/admin.py` - CustomUserAdmin bulk actions
- Django's built-in email system (no external dependencies required)
