"""URL patterns for the products app."""

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_product, name='add'),
    path('<int:pk>/', views.product_detail, name='detail'),
    path('<int:pk>/edit/', views.product_update, name='edit'),
    path('<int:pk>/delete/', views.product_delete, name='delete'),
]
