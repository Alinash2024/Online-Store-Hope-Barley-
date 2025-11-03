"""Models for the reviews app."""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from products.models import Product


class Review(models.Model):
    """Model representing a product review."""

    RATING_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for Review model."""
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        """String representation of the review."""
        return f'{self.product.name} - {self.user.username} - {self.rating}'

    def clean(self):
        """Validate the review instance."""
        pass

    def save(self, *args, **kwargs):
        """Save the review instance."""
        super().save(*args, **kwargs)

    def validate_user_purchase(self):
        """Validate that the user has purchased the product.

        Raises:
            ValidationError: If the user has not purchased the product.
        """
        if not self.user_has_purchased_product():
            raise ValidationError(
                "You can only review a product you have purchased."
            )

    def user_has_purchased_product(self):
        """Check if the user has purchased the product.

        Returns:
            bool: True if the user has purchased the product, False otherwise.
        """
        try:
            from orders.models import OrderItem
            return OrderItem.objects.filter(
                order__user=self.user,
                order__is_paid=True,
                product=self.product
            ).exists()
        except ImportError:
            return True
