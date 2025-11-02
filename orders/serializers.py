"""Serializers for the orders app.

This module defines the serializers for Order and OrderItem models,
handling the conversion between model instances and JSON representations
for the REST API.
"""

from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for the OrderItem model."""

    product = ProductSerializer(read_only=True)

    class Meta:
        """Meta options for OrderItemSerializer."""

        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for the Order model.

    Handles serialization of Order objects including nested OrderItem objects.
    Sets the user field to the currently authenticated user during creation.
    """

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        """Meta options for OrderSerializer."""

        model = Order
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
