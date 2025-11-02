"""API views for the orders app.

This module defines the REST API endpoints for managing orders.
It includes a ViewSet for Order objects with authentication required,
allowing users to manage only their own orders.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """API ViewSet for managing user orders.

    Provides standard CRUD operations for Order objects, but restricts
    access to orders belonging to the currently authenticated user.
    Requires authentication for all operations.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.none()

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
