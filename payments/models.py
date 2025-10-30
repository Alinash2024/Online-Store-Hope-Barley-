"""Models for the payments app.

This module defines the Payment, PaymentMethod, and Refund models
for handling payment transactions, methods, and refunds within the application.
"""

from django.db import models
from django.conf import settings
from orders.models import Order


class Payment(models.Model):
    """Model representing a payment transaction."""

    PAYMENT_METHOD_CHOICES = [
        ("credit_card", "Credit Card"),
        ("debit_card", "Debit Card"),
        ("paypal", "PayPal"),
        ("bank_transfer", "Bank Transfer"),
        ("digital_wallet", "Digital Wallet"),
        ("cash_on_delivery", "Cash on Delivery"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
        ("cancelled", "Cancelled"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="payment"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES
    )
    status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )
    transaction_id = models.CharField(
        max_length=100, unique=True, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    payment_date = models.DateTimeField(blank=True, null=True)
    gateway_response = models.TextField(
        blank=True, null=True
    )

    def __str__(self):
        """Return string representation of the payment."""
        return f"Payment {self.id} for Order {self.order.id}"

    def get_payment_method_display(self):
        return dict(self.PAYMENT_METHOD_CHOICES).get(
            self.payment_method, self.payment_method
        )

    def get_status_display(self):
        return dict(self.PAYMENT_STATUS_CHOICES).get(self.status, self.status)

    @property
    def is_successful(self):
        return self.status == "completed"

    @property
    def is_pending(self):
        return self.status == "pending"

    @property
    def is_failed(self):
        return self.status == "failed"

    class Meta:
        """Meta options for Payment model."""
        ordering = ["-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"


class PaymentMethod(models.Model):
    """Model representing a payment method available to users."""

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return string representation of the payment method."""
        return self.name

    class Meta:
        """Meta options for PaymentMethod model."""
        ordering = ["name"]
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"


class Refund(models.Model):
    """Model representing a refund for a payment."""

    REFUND_STATUS_CHOICES = [
        ("requested", "Requested"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name="refunds"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(
        max_length=20, choices=REFUND_STATUS_CHOICES, default="requested"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        """Return string representation of the refund."""
        return f"Refund {self.id} for Payment {self.payment.id}"

    def get_status_display(self):
        return dict(self.REFUND_STATUS_CHOICES).get(self.status, self.status)

    class Meta:
        """Meta options for Refund model."""
        ordering = ["-created_at"]
        verbose_name = "Refund"
        verbose_name_plural = "Refunds"
