"""
Tests for GraphQL product mutations.

This module contains tests for the 'createProduct' GraphQL mutation,
verifying its behavior under different user permissions (admin vs.
regular user).
"""

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from graphene.test import Client as GrapheneClient
from .schema import schema

User = get_user_model()


class TestGraphQLProductMutations(TestCase):
    """
    Test suite for GraphQL mutations related to Product creation.

    This class tests the 'createProduct' GraphQL mutation,
    verifying its behavior under different user permissions
    (admin vs. regular user).
    """

    def setUp(self) -> None:
        """
        Set up necessary objects for tests.

        Creates admin and regular users with specific permissions.
        Initializes the GraphQL test client using the project's schema.
        Initializes RequestFactory for creating mock requests.
        """
        self.factory = RequestFactory()
        self.admin_user = User.objects.create_user(
            email="admin_test@example.com",
            password="testpass123",
            is_staff=True,
            is_superuser=True,
        )

        self.regular_user = User.objects.create_user(
            email="regular_test@example.com",
            password="testpass123",
            is_staff=False,
        )

        self.client = GrapheneClient(schema)

    def get_mock_request(self, user):
        request = self.factory.get("/")
        request.user = user
        return request

    def test_create_product_mutation_as_admin(self) -> None:
        mutation = """
            mutation($name: String!, $price: Decimal!, $description: String!) {
                createProduct(name: $name, price: $price, description: $description) {
                    product {
                        id
                        name
                        price
                        description
                        isActive
                    }
                }
            }
        """
        variables = {
            "name": "New Test Product",
            "price": "9.99",
            "description": "A test product for mutation",
        }

        mock_request = self.get_mock_request(self.admin_user)

        response = self.client.execute(
            mutation, variables=variables, context_value=mock_request
        )

        self.assertNotIn(
            "errors",
            response,
            msg=f"GraphQL mutation failed with errors: {response.get('errors')}",
        )

        data = (
            response.get("data", {})
            .get("createProduct", {})
            .get("product", {})
        )

        self.assertEqual(data["name"], variables["name"])
        self.assertEqual(data["price"], variables["price"])
        self.assertEqual(data["description"], variables["description"])
        self.assertTrue(data["isActive"])

    def test_create_product_mutation_as_regular_user(self) -> None:
        mutation = """
            mutation($name: String!, $price: Decimal!, $description: String!) {
                createProduct(name: $name, price: $price, description: $description) {
                    product {
                        id
                        name
                    }
                }
            }
        """
        variables = {
            "name": "Unauthorized Product",
            "price": "9.99",
            "description": "Should not be created",
        }

        mock_request = self.get_mock_request(self.regular_user)

        response = self.client.execute(
            mutation, variables=variables, context_value=mock_request
        )

        self.assertIn(
            "errors",
            response,
            msg="Expected an error for unauthorized mutation, but got none.",
        )

        error_messages = [
            str(error.get("message", ""))
            for error in response.get("errors", [])
        ]
        authorization_error_found = any(
            "permission" in msg.lower()
            or "auth" in msg.lower()
            or "not authorized" in msg.lower()
            for msg in error_messages
        )
        self.assertTrue(
            authorization_error_found,
            msg=f"Expected an authorization error, but got: {response['errors']}",
        )
