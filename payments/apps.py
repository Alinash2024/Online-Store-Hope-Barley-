"""
App configuration for the payments application.

This module defines the configuration for the 'payments' app,
including its name and default settings for Django models.
"""

from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """AppConfig for the payments application."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "payments"
