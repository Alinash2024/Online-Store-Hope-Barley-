"""App configuration for the users application."""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """App config for the users app."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
