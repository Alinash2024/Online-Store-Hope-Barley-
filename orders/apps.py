"""Apps configuration for the orders app.

This module defines the application configuration for the orders app,
specifying the default auto field and the name of the app.
"""

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Configuration class for the orders app.

    Sets the default auto field to BigAutoField and defines the app name.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
