"""App configuration for the products application."""

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """AppConfig for the products application."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "products"
