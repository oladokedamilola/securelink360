# accounts/urls.py
from django.urls import path
from .views import register, CustomLoginView
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout")
]
