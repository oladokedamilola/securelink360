# networks/urls_visual.py
from django.urls import path
from .views_visual import live_network

urlpatterns = [
    path("<int:network_id>/live/", live_network, name="network_live"),
]
