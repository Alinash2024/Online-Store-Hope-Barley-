"""Tests for the products app models and API views."""

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Product

User = get_user_model()


class ProductModelTest(TestCase):
    """Test suite for Product model."""

    def setUp(self):
        self.product = Product.objects.create(
            name='Test Coffee',
            price=15.99,
            description='Test coffee description'
        )

    def test_product_creation(self):
        """Test creating a product instance."""
        self.assertEqual(self.product.name, 'Test Coffee')
        self.assertEqual(self.product.price, 15.99)


class ProductAPITest(APITestCase):
    """Test suite for Product API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Test Coffee',
            price=15.99,
            description='Test coffee description'
        )

    def test_get_products(self):
        """Test retrieving a list of products."""
        self.client.force_authenticate(user=self.user)

        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_product_detail(self):
        """Test retrieving a specific product."""
        self.client.force_authenticate(user=self.user)

        url = reverse('product-detail', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
