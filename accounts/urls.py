# accounts/urls.py
from django.urls import path
from .views import register, custom_login, custom_logout, edit_profile

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", custom_login, name="login"),
    path("logout/", custom_logout, name="logout"),

    path("profile/edit/", edit_profile, name="edit_profile"),

]
