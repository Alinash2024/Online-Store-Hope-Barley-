"""Tests for the users app models and API views."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

User = get_user_model()


class UserModelTest(TestCase):
    """Test suite for the User model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

    def test_user_creation(self):
        """Test creating a user instance."""
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)


class UserAPITest(TestCase):
    """Test suite for user API endpoints like registration and login."""

    def setUp(self):
        self.client = Client()

    def test_register_user(self):
        """Test user registration via API."""
        initial_count = User.objects.count()

        url = reverse("users:register")
        data = {
            "email": "new@example.com",
            "password1": "newpass123",
            "password2": "newpass123",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)

        self.assertEqual(User.objects.count(), initial_count + 1)

        new_user = User.objects.get(email="new@example.com")
        self.assertEqual(new_user.email, "new@example.com")

    def test_login_user(self):
        """Test user login via API."""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )

        url = reverse("users:login")
        data = {
            "username": "test@example.com",
            "password": "testpass123",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(email="test@example.com")
        self.assertTrue(user.check_password("testpass123"))
