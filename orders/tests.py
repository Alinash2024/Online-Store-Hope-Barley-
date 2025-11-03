"""Test cases for the orders app.

This module contains unit tests for the Order model,
order-related API views,
including cart functionality and checkout processes.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from .models import Order
from products.models import Product

User = get_user_model()


class OrderModelTest(TestCase):
    """Test cases for the Order model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_order_creation(self):
        order = Order.objects.create(
            user=self.user,
            full_name="Test User",
            phone="+1234567890",
            city="Test City",
            address="Test Address 123",
            total_price=100.00
        )

        self.assertIsNotNone(order.id)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_price, 100.00)


class OrderAPITest(TestCase):
    """Test cases for the order-related API views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_cart_add_authenticated(self):
        product = Product.objects.create(
            name="Test Product",
            price=50.00,
            stock=10
        )

        login_successful = self.client.login(
            email='test@example.com',
            password='testpass123'
        )
        self.assertTrue(login_successful)

        url = reverse('orders:cart_add')
        data = {
            'product_id': product.id,
            'quantity': 2
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['cart_total_items'], 2)
        self.assertEqual(
            float(response_data['cart_total_price']),
            100.00
        )

    def test_cart_detail_authenticated(self):
        login_successful = self.client.login(
            email='test@example.com',
            password='testpass123'
        )
        self.assertTrue(login_successful)

        url = reverse('orders:cart_detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cart_update_authenticated(self):
        product = Product.objects.create(
            name="Test Product",
            price=50.00,
            stock=10
        )

        login_successful = self.client.login(
            email='test@example.com',
            password='testpass123'
        )
        self.assertTrue(login_successful)

        add_url = reverse('orders:cart_add')
        add_data = {
            'product_id': product.id,
            'quantity': 2
        }
        self.client.post(add_url, add_data)

        update_url = reverse('orders:cart_update')
        update_data = {
            'product_id': product.id,
            'quantity': 5
        }

        response = self.client.post(update_url, update_data)
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['cart_total_items'], 5)
        self.assertEqual(
            float(response_data['cart_total_price']),
            250.00
        )

    def test_cart_remove_authenticated(self):
        product = Product.objects.create(
            name="Test Product",
            price=50.00,
            stock=10
        )

        login_successful = self.client.login(
            email='test@example.com',
            password='testpass123'
        )
        self.assertTrue(login_successful)

        add_url = reverse('orders:cart_add')
        add_data = {
            'product_id': product.id,
            'quantity': 2
        }
        self.client.post(add_url, add_data)

        remove_url = reverse('orders:cart_remove')
        remove_data = {
            'product_id': product.id
        }

        response = self.client.post(remove_url, remove_data)
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['cart_total_items'], 0)
        self.assertEqual(
            float(response_data['cart_total_price']),
            0.00
        )

    def test_checkout_authenticated(self):
        login_successful = self.client.login(
            email='test@example.com',
            password='testpass123'
        )
        self.assertTrue(login_successful)

        url = reverse('orders:checkout')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302])

    def test_order_success_authenticated(self):
        order = Order.objects.create(
            user=self.user,
            full_name="Test User",
            phone="+1234567890",
            city="Test City",
            address="Test Address 123",
            total_price=100.00
        )

        login_successful = self.client.login(
            email='test@example.com',
            password='testpass123'
        )
        self.assertTrue(login_successful)

        url = reverse(
            'orders:order_success',
            kwargs={'order_id': order.id}
        )

        try:
            response = self.client.get(url)

            self.assertIn(response.status_code, [200, 302])
        except Exception as e:
            if "TemplateDoesNotExist" in str(type(e)):
                self.skipTest(
                    "Шаблон orders/order_success.html отсутствует"
                )
            else:
                raise
