from django.urls import path
from . import views

urlpatterns = [
    path("my-devices/", views.my_devices, name="my_devices"),
    path("device/<int:pk>/update/", views.update_device, name="update_device"),
    path("device/<int:pk>/delete/", views.delete_device, name="delete_device"),
    path('register-device/', views.register_device, name='register_device'),
]
