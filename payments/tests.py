"""Tests for the payments app models and views."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from decimal import Decimal
import json
from .models import Payment, PaymentMethod, Refund
from orders.models import Order

User = get_user_model()


class PaymentModelTest(TestCase):
    """Test suite for Payment, PaymentMethod, and Refund models."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        self.order = Order.objects.create(
            user=self.user,
            full_name="Test User",
            phone="+1234567890",
            city="Test City",
            address="Test Address 123",
            total_price=Decimal("100.00"),
        )

    def test_payment_creation(self):
        """Test creating a payment."""
        payment = Payment.objects.create(
            order=self.order,
            user=self.user,
            amount=Decimal("100.00"),
            payment_method="credit_card",
            status="pending",
            transaction_id="TEST123456789",
        )

        self.assertIsNotNone(payment.id)
        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.amount, Decimal("100.00"))
        self.assertEqual(payment.payment_method, "credit_card")
        self.assertEqual(payment.status, "pending")
        self.assertEqual(payment.transaction_id, "TEST123456789")
        self.assertEqual(
            str(payment), f"Payment {payment.id} for Order {self.order.id}"
        )

    def test_payment_method_creation(self):
        """Test creating a payment method."""
        payment_method = PaymentMethod.objects.create(
            name="Test Payment Method",
            description="Test description",
            is_active=True,
        )

        self.assertIsNotNone(payment_method.id)
        self.assertEqual(payment_method.name, "Test Payment Method")
        self.assertEqual(payment_method.description, "Test description")
        self.assertTrue(payment_method.is_active)
        self.assertEqual(str(payment_method), "Test Payment Method")

    def test_refund_creation(self):
        """Test creating a refund."""
        payment = Payment.objects.create(
            order=self.order,
            user=self.user,
            amount=Decimal("100.00"),
            payment_method="credit_card",
            status="completed",
            transaction_id="TEST123456789",
        )

        refund = Refund.objects.create(
            payment=payment,
            amount=Decimal("50.00"),
            reason="Test refund reason",
            status="requested",
        )

        self.assertIsNotNone(refund.id)
        self.assertEqual(refund.payment, payment)
        self.assertEqual(refund.amount, Decimal("50.00"))
        self.assertEqual(refund.reason, "Test refund reason")
        self.assertEqual(refund.status, "requested")
        self.assertEqual(
            str(refund), f"Refund {refund.id} for Payment {payment.id}"
        )


class PaymentViewTest(TestCase):
    """Test suite for payment-related views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        self.order = Order.objects.create(
            user=self.user,
            full_name="Test User",
            phone="+1234567890",
            city="Test City",
            address="Test Address 123",
            total_price=Decimal("100.00"),
            status="pending",
        )

        self.payment = Payment.objects.create(
            order=self.order,
            user=self.user,
            amount=Decimal("100.00"),
            payment_method="credit_card",
            status="pending",
            transaction_id="TEST123456789",
        )

    def test_payment_process_view_get(self):
        """Test GET request to the payment processing page."""
        login_successful = self.client.login(
            email="test@example.com", password="testpass123"
        )
        self.assertTrue(login_successful)

        url = reverse(
            "payments:payment_process", kwargs={"order_id": self.order.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_payment_process_view_post_success(self):
        """Test successful payment via POST request."""
        login_successful = self.client.login(
            email="test@example.com", password="testpass123"
        )
        self.assertTrue(login_successful)

        url = reverse(
            "payments:payment_process", kwargs={"order_id": self.order.id}
        )
        data = {
            "payment_method": "credit_card",
            "card_number": "1234 5678 9012 3456",
            "expiry_date": "12/25",
            "cvv": "123",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "completed")
        self.assertEqual(self.payment.payment_method, "credit_card")

    def test_payment_process_view_post_invalid_data(self):
        """Test payment with invalid data."""
        login_successful = self.client.login(
            email="test@example.com", password="testpass123"
        )
        self.assertTrue(login_successful)

        url = reverse(
            "payments:payment_process", kwargs={"order_id": self.order.id}
        )
        data = {
            "payment_method": "credit_card",
            "card_number": "123",
            "expiry_date": "12/25",
            "cvv": "123",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_payment_webhook_view(self):
        """Test webhook for handling payment gateway notifications."""
        url = reverse("payments:payment_webhook")

        data = {
            "event_type": "payment.completed",
            "transaction_id": "TEST123456789",
        }

        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "completed")
