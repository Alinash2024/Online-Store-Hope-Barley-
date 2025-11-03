# products/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse
from typing import Optional


class Product(models.Model):
    """Model representing a product in the store."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_path = models.CharField(max_length=255, blank=True,
                                  null=True)
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, default='item')

    class Meta:
        ordering = ['name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self) -> str:
        """
        String representation of the product.

        Returns:
            str: Product name
        """
        return self.name

    @property
    def image_url(self) -> Optional[str]:
        """
        Get the image URL.

        Returns:
            str or None: URL to the image or None if no image path
        """
        if self.image_path and self.image_path.strip():
            return f"{settings.STATIC_URL}{self.image_path}"
        return None

    @property
    def is_in_stock(self) -> bool:
        """
        Check if product is in stock.

        Returns:
            bool: True if product is active and in stock, False otherwise
        """
        return self.stock > 0 and self.is_active

    @property
    def stock_status(self) -> str:
        """
        Get text status of product stock.

        Returns:
            str: Stock status message
        """
        if not self.is_active:
            return 'Unavailable'
        elif self.stock == 0:
            return 'Out of stock'
        elif self.stock < 5:
            return 'Low stock'
        else:
            return 'In stock'

    def get_absolute_url(self) -> str:
        """
        Get absolute URL for the product.

        Returns:
            str: Absolute URL to product detail page
        """
        return reverse('products:detail', kwargs={'pk': self.pk})

    def can_be_ordered(self, quantity: int = 1) -> bool:
        """
        Check if specified quantity can be ordered.

        Args:
            quantity: Quantity to check

        Returns:
            bool: True if product can be ordered, False otherwise
        """
        return self.is_active and self.stock >= quantity

    def decrease_stock(self, quantity: int) -> bool:
        """
        Decrease product stock.

        Args:
            quantity: Quantity to decrease by

        Returns:
            bool: True if stock was decreased, False otherwise
        """
        if self.can_be_ordered(quantity):
            self.stock -= quantity
            self.save()
            return True
        return False

    def increase_stock(self, quantity: int) -> None:
        """
        Increase product stock.

        Args:
            quantity: Quantity to increase by
        """
        self.stock += quantity
        self.save()
