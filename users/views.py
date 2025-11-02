"""Views for the users app including registration, login."""

from django.shortcuts import render, redirect
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from products.models import Product
from orders.models import Order
from orders.cart import Cart
from .forms import (
    LoginForm,
    RegistrationForm,
    UserProfileForm,
    PasswordChangeCustomForm,
    ForgotPasswordForm,
)
from django.conf import settings


def home(request):
    """
    Главная страница с каталогом продуктов
    """
    products = Product.objects.filter(is_active=True)

    search_query = request.GET.get("search")
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    category = request.GET.get("category")
    if category:
        products = products.filter(category=category)

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort_by = request.GET.get(
        "sort", "created_at"
    )
    if sort_by == "price_asc":
        products = products.order_by("price")
    elif sort_by == "price_desc":
        products = products.order_by("-price")
    elif sort_by == "created_at":
        products = products.order_by("-created_at")
    elif sort_by == "stock":
        products = products.order_by("-stock")
    else:
        products = products.order_by(
            "-created_at"
        )

    paginator = Paginator(products, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "products": page_obj,
        "search_query": search_query,
        "selected_category": category,
        "min_price": min_price,
        "max_price": max_price,
        "sort_by": sort_by,
    }

    return render(request, "users/home.html", context)


def register(request):
    """
    Регистрация нового пользователя
    """
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get("email")
            messages.success(request, f"Account created for {email}!")
            login(request, user)
            return redirect("users:home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    """
    Вход пользователя в систему
    """
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {email}!")
                next_page = request.GET.get(
                    "next", settings.LOGIN_REDIRECT_URL or "users:home"
                )
                return redirect(next_page)
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("users:home")


@login_required
def account_view(request):
    """
    Страница аккаунта пользователя
    """

    orders_list = Order.objects.filter(user=request.user).order_by(
        "-created_at"
    )

    paginator = Paginator(orders_list, 5)
    page_number = request.GET.get("page")
    orders = paginator.get_page(page_number)

    cart = Cart(request)

    if request.method == "POST":
        if "save_profile" in request.POST:
            profile_form = UserProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(
                    request, "Your profile has been updated successfully!"
                )
                return redirect("users:account")
            else:
                messages.error(request, "Please correct the errors below.")
        elif "change_password" in request.POST:
            password_form = PasswordChangeCustomForm(
                request.user, request.POST
            )
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(
                    request, user
                )
                messages.success(
                    request, "Your password was successfully updated!"
                )
                return redirect("users:account")
            else:
                messages.error(request, "Please correct the errors below.")
    else:
        profile_form = UserProfileForm(instance=request.user)
        password_form = PasswordChangeCustomForm(request.user)

    context = {
        "orders": orders,
        "profile_form": profile_form,
        "password_form": password_form,
        "cart": cart,
    }

    return render(request, "users/account.html", context)


def forgot_password(request):
    """
    Страница восстановления пароля
    """
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():

            email = form.cleaned_data["email"]
            messages.success(
                request,
                f"Instructions to reset your "
                f"password have been sent to {email}.",
            )
            return redirect("users:login")
        else:
            messages.error(request, "Please enter a valid email address.")
    else:
        form = ForgotPasswordForm()

    return render(request, "users/forgot_password.html", {"form": form})


def guides_recipes(request):
    """
    Страница с руководствами и рецептами
    """
    return render(request, "users/guides-recipes.html")
