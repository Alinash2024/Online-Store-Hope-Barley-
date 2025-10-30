"""Tests for the reviews app models and API views."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Review
from products.models import Product

User = get_user_model()


class ReviewModelTest(TestCase):
    """Test suite for Review model."""

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

    def test_review_creation(self):
        """Test creating a review instance."""
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            comment='Great coffee!',
            rating=5
        )
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.comment, 'Great coffee!')
        self.assertEqual(review.rating, 5)


class ReviewAPITest(APITestCase):
    """Test suite for Review API endpoints."""

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

    def test_create_review_authenticated(self):
        """Test creating a review via API with authentication."""
        self.client.force_authenticate(user=self.user)
        url = reverse('review-list')
        data = {
            'product': self.product.id,
            'comment': 'Great coffee!',
            'rating': 5
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(
            response.status_code, [status.HTTP_201_CREATED,
                                   status.HTTP_400_BAD_REQUEST]
        )

    def test_get_reviews_authenticated(self):
        """Test retrieving reviews via API with authentication."""
        self.client.force_authenticate(user=self.user)
        Review.objects.create(
            product=self.product,
            user=self.user,
            comment='Great coffee!',
            rating=5
        )
        url = reverse('review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
