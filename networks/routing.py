# networks/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/network/(?P<network_id>\w+)/monitor/$', consumers.NetworkVisualizationConsumer.as_asgi()),
    re_path(r'^ws/network/join/$', consumers.NetworkJoinConsumer.as_asgi()),
]