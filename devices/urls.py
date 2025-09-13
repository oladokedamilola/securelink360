from django.urls import path
from . import views

urlpatterns = [
    path('device_list/', views.device_list, name='device_list'),
    path('register-device/', views.register_device, name='register_device'),
]
