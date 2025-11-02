"""URL patterns for the reviews app."""

from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('product/<int:product_id>/review/',
         views.add_review, name='add_review'),
]
