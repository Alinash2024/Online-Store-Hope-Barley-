"""Models for the orders app.

This module defines the Order and OrderItem models for managing
customer orders, including their status, items, and related calculations.
"""

from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from products.models import Product
from decimal import Decimal
from typing import Dict, Any, Optional


class Order(models.Model):
    """Model representing a customer order."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Shipping fields
    full_name = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=100, default='')
    address = models.TextField(default='')
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('debit', 'Debit Card'),
            ('wallet', 'Digital Wallet'),
            ('cod', 'Cash On Delivery'),
        ]
    )

    # Analytics fields
    completed_at = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    @property
    def total_amount(self) -> Decimal:
        """
        Get the total amount of the order.

        Returns:
            Decimal: The total price of the order
        """
        return self.total_price

    @property
    def payment_status(self) -> Optional[str]:
        """
        Get the payment status for the order.

        Returns:
            str or None: Payment status or None if no payment exists
        """
        try:
            return self.payment.status
        except AttributeError:
            return None

    @property
    def is_payment_completed(self) -> bool:
        """
        Check if payment is completed.

        Returns:
            bool: True if payment is completed, False otherwise
        """
        try:
            return self.payment.status == 'completed'
        except AttributeError:
            return False

    def __str__(self) -> str:
        """
        Return string representation of the order.

        Returns:
            str: Order ID and username
        """
        return f"Order {self.id} - {self.user.username}"

    @classmethod
    @transaction.atomic
    def create_from_cart(
        cls,
        user: settings.AUTH_USER_MODEL,
        cart: Any,
        shipping_data: Dict[str, str]
    ) -> 'Order':
        """
        Create an order from cart with atomic transaction.

        Args:
            user: The user placing the order
            cart: Cart object containing items
            shipping_ Dictionary with shipping information

        Returns:
            Order: The created order object
        """
        # Create order
        order = cls.objects.create(
            user=user,
            total_price=cart.get_total_price(),
            full_name=shipping_data['full_name'],
            phone=shipping_data['phone'],
            city=shipping_data['city'],
            address=shipping_data['address'],
            payment_method=shipping_data['payment_method']
        )

        # Create order items and update stock
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )

            # Update product stock
            item['product'].stock -= item['quantity']
            item['product'].save()

        return order

    def get_revenue(self) -> Decimal:
        """
        Get revenue from order (if paid).

        Returns:
            Decimal: Revenue amount or 0.00 if not paid
        """
        if self.is_paid:
            return self.total_price
        return Decimal('0.00')

    def get_items_count(self) -> int:
        """
        Get total number of items in order.

        Returns:
            int: Total quantity of items
        """
        return self.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    def mark_as_completed(self) -> None:
        """
        Mark order as completed.

        Raises:
            ValueError: If order is not delivered
        """
        if self.status != 'delivered':
            raise ValueError(
                "Order must be delivered before marking as completed"
            )
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def cancel_order(self) -> None:
        """
        Cancel order and return items to stock.

        Raises:
            ValueError: If order status is not pending or processing
        """
        if self.status not in ['pending', 'processing']:
            raise ValueError(
                "Can only cancel pending or processing orders"
            )

        # Return items to stock
        for item in self.items.all():
            item.product.stock += item.quantity
            item.product.save()

        self.status = 'cancelled'
        self.save()

        # Also cancel payment if exists
        try:
            if self.payment.status == 'completed':
                self.payment.status = 'refunded'
                self.payment.save()
        except AttributeError:
            pass

    class Meta:
        """Meta options for Order model."""

        ordering = ['-created_at']


class OrderItem(models.Model):
    """Model representing an item in an order."""

    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        """
        Return string representation of the order item.

        Returns:
            str: Quantity and product name
        """
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self) -> Decimal:
        """
        Calculate total price for this item.

        Returns:
            Decimal: Total price (quantity * price)
        """
        return self.quantity * self.price

    @property
    def revenue(self) -> Decimal:
        """
        Get revenue from this order item.

        Returns:
            Decimal: Revenue amount or 0.00 if order is not paid
        """
        if self.order.is_paid:
            return self.get_total_price()
        return Decimal('0.00')

    @property
    def profit(self) -> Decimal:
        """
        Get profit from this order item (if Product has cost field).

        Returns:
            Decimal: Profit amount or 0.00 if cost field doesn't exist
        """
        try:
            return (self.price - self.product.cost) * self.quantity
        except (AttributeError, TypeError):
            return Decimal('0.00')

    class Meta:
        """Meta options for OrderItem model."""

        ordering = ['-order__created_at']
