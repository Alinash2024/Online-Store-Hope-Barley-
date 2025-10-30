"""URL configuration for the orders app.

This module defines the URL patterns for the orders app,
including cart management, checkout, and order success views.
"""

from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/state/', views.cart_state, name='cart_state'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success,
         name='order_success'
         ),
]
