from django.urls import path
from . import views

app_name = 'shortener'

urlpatterns = [
    path('', views.home, name='home'),
    path('stats/<str:short_code>/', views.stats, name='stats'),
    path('<str:short_code>/', views.redirect_url, name='redirect'),
]