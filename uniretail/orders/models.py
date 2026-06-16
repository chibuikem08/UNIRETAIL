from django.db import models
from django.conf import settings
from shops.models import Product


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING   = 'PENDING',   'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        READY     = 'READY',     'Ready for Pickup'
        COMPLETED = 'COMPLETED', 'Picked Up'
        CANCELLED = 'CANCELLED', 'Cancelled'

    buyer       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status      = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    note        = models.TextField(blank=True, help_text='Special instructions for the vendor')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.pk} by {self.buyer.username} — {self.status}"

    def compute_total(self):
        self.total_price = sum(item.subtotal for item in self.items.all())
        self.save(update_fields=['total_price'])

    @property
    def can_cancel(self):
        return self.status == self.Status.PENDING

    @property
    def item_count(self):
        return self.items.count()


class OrderItem(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product    = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity   = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot at time of order

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


class Cart(models.Model):
    """Persistent cart tied to a logged-in user."""
    user       = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.cart_items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.cart_items.all())

    def clear(self):
        self.cart_items.all().delete()


class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product  = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity
