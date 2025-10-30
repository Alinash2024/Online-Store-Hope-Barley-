from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from typing import Any, Dict, Optional


class CustomUserManager(BaseUserManager["User"]):
    """Custom manager for user model without username."""

    def create_user(
        self,
        email: str,
        password: Optional[str] = None,
        **extra_fields: Dict[str, Any]
    ) -> "User":
        """
        Create and return a regular user with an email and password.

        Args:
            email: User's email address
            password: User's password
            **extra_fields: Additional fields for the user

        Returns:
            User: Created user object

        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: Optional[str] = None,
        **extra_fields: Dict[str, Any]
    ) -> "User":
        """
        Create and return a superuser with an email and password.

        Args:
            email: Superuser's email address
            password: Superuser's password
            **extra_fields: Additional fields for the superuser

        Returns:
            User: Created superuser object
        """
        # noinspection PyTypeChecker
        extra_fields.setdefault("is_staff", True)
        # noinspection PyTypeChecker
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model using email instead of username."""

    username = None  # Remove username field
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self) -> str:
        """
        String representation of the user.

        Returns:
            str: User's email
        """
        return self.email
