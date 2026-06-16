from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Extended user model supporting three roles:
    - STUDENT: Can browse shops, place and pay for orders
    - STAFF:   Same as student (university staff member)
    - VENDOR:  Can manage a shop and its products, fulfill orders
    - ADMIN:   Full access (uses Django's is_staff / superuser flags too)
    """

    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        STAFF   = 'STAFF',   'Staff'
        VENDOR  = 'VENDOR',  'Vendor'
        ADMIN   = 'ADMIN',   'Admin'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    # Extra profile fields
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(
        upload_to='profiles/', blank=True, null=True
    )

    # Vendor-specific: admin must approve before the vendor can sell
    is_approved_vendor = models.BooleanField(default=False)

    # Timestamps
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    # ── Convenience helpers ──────────────────────────────────────────────────
    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_university_staff(self):
        return self.role == self.Role.STAFF

    @property
    def is_vendor(self):
        return self.role == self.Role.VENDOR

    @property
    def is_site_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def can_shop(self):
        """Students and staff can place orders."""
        return self.role in (self.Role.STUDENT, self.Role.STAFF)
