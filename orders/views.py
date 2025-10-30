"""Views for the orders app.

This module handles order-related views including cart management,
checkout process, order confirmation, and admin analytics.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.db.models import Sum, Count, F
from products.models import Product
from .cart import Cart
from .models import Order, OrderItem
from datetime import timedelta
from django.utils import timezone
from typing import Any, Dict


@require_POST
def cart_add(request: HttpRequest) -> JsonResponse:
    try:
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        if not product_id or not quantity:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request data'
            }, status=400)

        product = get_object_or_404(Product, id=product_id)

        if product.stock < quantity:
            return JsonResponse({
                'success': False,
                'message': f'Not enough stock. Available: {product.stock}'
            }, status=400)

        cart = Cart(request)

        cart.add(product=product, quantity=quantity, override_quantity=False)

        cart.save()

        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart',
            'cart_total_items': len(cart),
            'cart_total_price': str(cart.get_total_price())
        })

    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Error adding product to cart'
        }, status=500)


@require_POST
def cart_update(request: HttpRequest) -> JsonResponse:
    try:
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 0))

        if not product_id or quantity < 0:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request data'
            }, status=400)

        cart = Cart(request)

        product = get_object_or_404(Product, id=product_id)

        if quantity == 0:
            cart.remove(product)
        else:
            cart.add(product=product, quantity=quantity,
                     override_quantity=True)

        cart.save()

        return JsonResponse({
            'success': True,
            'message': 'Cart updated successfully',
            'cart_total_items': len(cart),
            'cart_total_price': str(cart.get_total_price())
        })

    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Error updating cart'
        }, status=500)


@require_POST
def cart_remove(request: HttpRequest) -> JsonResponse:
    try:
        product_id = request.POST.get('product_id')

        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request data'
            }, status=400)

        cart = Cart(request)

        product = get_object_or_404(Product, id=product_id)

        cart.remove(product)

        cart.save()

        return JsonResponse({
            'success': True,
            'message': 'Product removed from cart',
            'cart_total_items': len(cart),
            'cart_total_price': str(cart.get_total_price())
        })

    except Exception:
        return JsonResponse({
            'success': False,
            'message': 'Error removing product from cart'
        }, status=500)


def cart_detail(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_data: Dict[str, Dict[str, Any]] = {}
        for item in cart:
            if 'product' in item and hasattr(item['product'], 'id'):
                product_id = str(item['product'].id)
                cart_data[product_id] = {
                    'quantity': item['quantity'],
                    'price': str(item['price'])
                }
        return JsonResponse({'cart': cart_data})

    return render(request, 'orders/cart.html', {'cart': cart})


def cart_state(request: HttpRequest) -> JsonResponse:
    cart = Cart(request)
    cart_data: Dict[str, Dict[str, Any]] = {}

    for item in cart:
        if 'product' in item and hasattr(item['product'], 'id'):
            product_id = str(item['product'].id)
            cart_data[product_id] = {
                'quantity': item['quantity'],
                'price': str(item['price'])
            }

    return JsonResponse({'cart': cart_data})


@login_required
def checkout(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)

    if not cart:
        messages.info(request, 'Ваша корзина пуста')
        return redirect('orders:cart_detail')

    unavailable_items = []
    for item in cart:
        if item['product'].stock < item['quantity']:
            product_name = item['product'].name
            available_stock = item['product'].stock
            unavailable_items.append(
                f"{product_name} "
                f"(доступно: {available_stock})"
            )

    if unavailable_items:
        unavailable_items_str = ", ".join(unavailable_items)
        messages.error(
            request,
            f'Недостаточно товаров на складе: '
            f'{unavailable_items_str}'
        )
        return redirect('orders:cart_detail')

    if request.method == 'POST':
        shipping_data = {
            'full_name': request.POST.get('full_name', '').strip(),
            'phone': request.POST.get('phone', '').strip(),
            'city': request.POST.get('city', '').strip(),
            'address': request.POST.get('address', '').strip(),
            'payment_method': request.POST.get('payment_method', 'debit')
        }

        errors = []
        if not shipping_data['full_name']:
            errors.append('Укажите полное имя')
        if not shipping_data['phone']:
            errors.append('Укажите номер телефона')
        if not shipping_data['city']:
            errors.append('Укажите город')
        if not shipping_data['address']:
            errors.append('Укажите адрес доставки')
        if shipping_data['payment_method'] not in ['debit', 'wallet', 'cod']:
            errors.append('Выберите способ оплаты')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'orders/checkout.html', {
                'cart': cart,
                'total_price': cart.get_total_price(),
                'shipping_data': shipping_data
            })

        try:
            with transaction.atomic():
                order = Order.create_from_cart(
                    request.user, cart, shipping_data
                )

            send_order_confirmation_email(order)
            send_admin_notification_email(order)

            cart.clear()

            order_id_str = str(order.id)
            messages.success(
                request,
                f'Заказ #{order_id_str} '
                f'успешно создан! Пожалуйста, завершите оплату.'
            )
            return redirect('payments:payment_process', order_id=order.id)

        except Exception:
            messages.error(
                request,
                'Произошла ошибка при создании заказа. '
                'Пожалуйста, попробуйте еще раз.'
            )
            return render(request, 'orders/checkout.html', {
                'cart': cart,
                'total_price': cart.get_total_price(),
                'shipping_data': shipping_data
            })

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'total_price': cart.get_total_price()
    })


@login_required
def order_success(request: HttpRequest, order_id: int) -> HttpResponse:
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        return render(request, 'orders/order_success.html', {'order': order})
    except Order.DoesNotExist:
        messages.error(request, 'Заказ не найден')
        return redirect('users:home')


@staff_member_required
def admin_order_analytics(request: HttpRequest) -> HttpResponse:
    total_revenue = Order.objects.filter(is_paid=True).aggregate(
        total=Sum('total_price')
    )['total'] or 0

    total_orders = Order.objects.count()

    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_revenue = Order.objects.filter(
        is_paid=True,
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('total_price'))['total'] or 0

    recent_orders = Order.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()

    top_products = OrderItem.objects.values(
        'product__name'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('price') * F('quantity'))
    ).order_by('-total_sold')[:10]

    orders_by_status = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')

    monthly_revenue = []
    for i in range(6):
        date = timezone.now() - timedelta(days=i * 30)
        month_start = date.replace(day=1, hour=0, minute=0,
                                   second=0, microsecond=0)

        if i > 0:
            next_month = (
                    date.replace(day=28) + timedelta(days=4)).replace(day=1)
            month_end = next_month - timedelta(seconds=1)
        else:
            month_end = timezone.now()

        monthly_data = Order.objects.filter(
            is_paid=True,
            created_at__gte=month_start,
            created_at__lte=month_end
        ).aggregate(
            total=Sum('total_price'),
            count=Count('id')
        )

        monthly_revenue.append({
            'month': month_start.strftime('%B %Y'),
            'total': monthly_data['total'] or 0,
            'count': monthly_data['count']
        })

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'recent_revenue': recent_revenue,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'orders_by_status': orders_by_status,
        'monthly_revenue': monthly_revenue,
    }

    return render(request, 'orders/analytics.html', context)


def send_order_confirmation_email(order: Order) -> None:
    subject = f'Подтверждение заказа #{order.id}'
    message_lines = [
        f'Здравствуйте, {order.full_name}!',
        '',
        f'Ваш заказ #{order.id} был успешно оформлен.',
        '',
        'Детали заказа:',
        f'Сумма: ${order.total_price}',
        f'Способ оплаты: {order.get_payment_method_display()}',
        '',
        'Адрес доставки:',
        order.city,
        order.address,
        '',
        f'Мы свяжемся с вами по телефону {order.phone} '
        f'для подтверждения деталей доставки.',
        '',
        'Спасибо за покупку!',
        'Команда Hop & Barley'
    ]
    message = '\n'.join(message_lines)

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )
    except Exception:
        pass


def send_admin_notification_email(order: Order) -> None:
    subject = f'Новый заказ #{order.id}'
    message_lines = [
        f'Новый заказ #{order.id} '
        f'от пользователя {order.user.username} ({order.user.email}).',
        '',
        'Детали заказа:',
        f'Сумма: ${order.total_price}',
        f'Способ оплаты: {order.get_payment_method_display()}',
        '',
        'Контактные данные:',
        f'Имя: {order.full_name}',
        f'Телефон: {order.phone}',
        f'Город: {order.city}',
        f'Адрес: {order.address}',
    ]
    message = '\n'.join(message_lines)

    try:
        admin_email = getattr(settings, 'ADMIN_EMAIL',
                              'admin@example.com')
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            fail_silently=False,
        )
    except Exception:
        pass
