from django.db import models
from django.conf import settings
from django.utils.text import slugify


class ShopCategory(models.TextChoices):
    FOOD        = 'FOOD',        'Food & Drinks'
    SNACKS      = 'SNACKS',      'Snacks & Provisions'
    STATIONERY  = 'STATIONERY',  'Stationery & Supplies'
    ELECTRONICS = 'ELECTRONICS', 'Electronics & Gadgets'
    CLOTHING    = 'CLOTHING',    'Clothing & Accessories'
    OTHER       = 'OTHER',       'Other'


class Shop(models.Model):
    vendor      = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shop'
    )
    name        = models.CharField(max_length=120)
    slug        = models.SlugField(max_length=140, unique=True, blank=True)
    category    = models.CharField(max_length=20, choices=ShopCategory.choices, default=ShopCategory.FOOD)
    description = models.TextField(blank=True)
    logo        = models.ImageField(upload_to='shop_logos/', blank=True, null=True)
    is_open     = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('shops:shop_detail', kwargs={'slug': self.slug})

    @property
    def product_count(self):
        return self.products.filter(is_available=True).count()


class ProductCategory(models.TextChoices):
    MEAL      = 'MEAL',      'Meals'
    DRINK     = 'DRINK',     'Drinks'
    SNACK     = 'SNACK',     'Snacks'
    PROVISION = 'PROVISION', 'Provisions'
    SUPPLY    = 'SUPPLY',    'Supplies'
    OTHER     = 'OTHER',     'Other'


class Product(models.Model):
    shop         = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    name         = models.CharField(max_length=120)
    slug         = models.SlugField(max_length=140, blank=True)
    category     = models.CharField(max_length=20, choices=ProductCategory.choices, default=ProductCategory.OTHER)
    description  = models.TextField(blank=True)
    price        = models.DecimalField(max_digits=10, decimal_places=2)
    image        = models.ImageField(upload_to='products/', blank=True, null=True)
    stock        = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('shop', 'slug')

    def __str__(self):
        return f"{self.name} — {self.shop.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('shops:product_detail', kwargs={'shop_slug': self.shop.slug, 'slug': self.slug})

    @property
    def in_stock(self):
        return self.stock > 0
