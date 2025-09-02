import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_network.settings')

application = get_asgi_application()




from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import notifications.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notifications.routing.websocket_urlpatterns
        )
    ),
})



import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from networks.consumers import NetworkConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_network.settings')

django_asgi_app = get_asgi_application()

websocket_urlpatterns = [
    path("ws/network/<int:network_id>/", NetworkConsumer.as_asgi()),
    # Optional: company-wide pipe
    path("ws/company/<int:company_id>/", NetworkConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
