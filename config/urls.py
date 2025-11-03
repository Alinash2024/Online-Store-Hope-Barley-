"""URL configuration for the project.

This module defines the URL patterns for the entire project.
It includes:
- Admin URLs
- Web interface pages (users, products, orders, reviews, payments)
- REST API endpoints (including user registration/login, and API endpoints
  for products, orders, and reviews registered via a DefaultRouter)
- API documentation endpoints (using drf-spectacular)
- GraphQL endpoint
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from users.api_views import register, login
from products.api_views import ProductViewSet
from orders.api_views import OrderViewSet
from reviews.api_views import ReviewViewSet
from shop_graphql.schema import schema
from graphene_django.views import GraphQLView

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet,  basename='order')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('users.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('reviews/', include('reviews.urls')),
    path('payments/', include('payments.urls')),

    path('api/users/register/', register),
    path('api/users/login/', login),
    path('api/', include(router.urls)),

    path('api/docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),


    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),
]
