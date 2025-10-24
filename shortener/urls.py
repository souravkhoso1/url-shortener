# shortener/urls.py
from django.urls import path
from . import views

app_name = 'shortener'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('my-urls/', views.my_urls, name='my_urls'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('stats/<str:short_code>/', views.stats, name='stats'),
    path('<str:short_code>/', views.redirect_url, name='redirect'),
]