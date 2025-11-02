"""Forms for the users app including login, registration, and profile."""

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    PasswordChangeForm,
)
from .models import User


class LoginForm(AuthenticationForm):
    """Form for user login using email and password."""

    username = forms.CharField(
        widget=forms.EmailInput(
            attrs={"class": "Input", "placeholder": "Enter your email"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "Input", "placeholder": "Enter your password"}
        )
    )
    remember_me = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email"


class RegistrationForm(UserCreationForm):
    """Form for user registration."""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "Input", "placeholder": "Enter your email"}
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "Input", "placeholder": "Create a password"}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "Input", "placeholder": "Confirm your password"}
        )
    )
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Password again"


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information."""

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "city",
            "address",
        )
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "Input",
                    "placeholder": "Enter your first name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={"class": "Input", "placeholder": "Enter your last name"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "Input", "placeholder": "Enter your email"}
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "Input",
                    "placeholder": "Enter your phone number",
                }
            ),
            "city": forms.TextInput(
                attrs={"class": "Input", "placeholder": "Enter your city"}
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "Textarea",
                    "placeholder": "Enter your shipping address",
                    "rows": 3,
                }
            ),
        }


class PasswordChangeCustomForm(PasswordChangeForm):
    """Custom form for changing user password."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs.update(
            {"class": "Input", "placeholder": "Enter current password"}
        )
        self.fields["new_password1"].widget.attrs.update(
            {"class": "Input", "placeholder": "Enter new password"}
        )
        self.fields["new_password2"].widget.attrs.update(
            {"class": "Input", "placeholder": "Confirm new password"}
        )


class ForgotPasswordForm(forms.Form):
    """Form for initiating password reset."""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "Input",
                "placeholder": "Enter your email address",
                "required": True,
            }
        )
    )
