from django.db import models
from django.conf import settings
from orders.models import Order


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING  = 'PENDING',  'Pending'
        SUCCESS  = 'SUCCESS',  'Successful'
        FAILED   = 'FAILED',   'Failed'

    order       = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    buyer       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    reference   = models.CharField(max_length=100, unique=True)
    status      = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    paid_at     = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.reference} — {self.status}"

    @property
    def is_successful(self):
        return self.status == self.Status.SUCCESS


class VendorBankAccount(models.Model):
    """
    Stores a vendor's bank details and their Paystack subaccount code.
    Created when vendor submits bank details.
    Subaccount is created on Paystack when admin approves the vendor.
    """
    vendor          = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bank_account'
    )
    bank_name       = models.CharField(max_length=100)
    bank_code       = models.CharField(max_length=20)  # Paystack bank code e.g. "044" for Access Bank
    account_number  = models.CharField(max_length=20)
    account_name    = models.CharField(max_length=120)  # Account holder's name as on the bank record
    bvn             = models.CharField(max_length=11, blank=True)  # Optional but recommended

    # Paystack subaccount details (filled after API call)
    subaccount_code  = models.CharField(max_length=100, blank=True)  # e.g. ACCT_xxxxxxxxxx
    subaccount_id    = models.CharField(max_length=100, blank=True)
    is_verified      = models.BooleanField(default=False)  # True once Paystack subaccount is created

    # Platform commission percentage (how much YOU keep per transaction)
    platform_charge_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.00,
        help_text="Percentage the platform keeps. e.g. 5.00 means vendor gets 95%"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor.username} — {self.bank_name} ({self.account_number})"

    @property
    def has_subaccount(self):
        return bool(self.subaccount_code)
