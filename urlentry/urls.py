from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<short_code>/", views.detail, name="views-detail")
]