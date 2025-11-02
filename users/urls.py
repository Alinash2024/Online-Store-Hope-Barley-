"""URL patterns for the users app."""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('account/', views.account_view, name='account'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('guides-recipes/', views.guides_recipes, name='guides_recipes'),
]
