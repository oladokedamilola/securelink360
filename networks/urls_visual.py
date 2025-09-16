# networks/urls_visual.py
from django.urls import path
from .views_visual import live_network

urlpatterns = [
    path("<int:network_id>/live/", live_network, name="network_live"),
]

# networks/urls_visual.py
from django.urls import path
from . import views_visual

urlpatterns = [
    # Live network monitoring dashboard
    path('network/<int:network_id>/monitor/', views_visual.live_network, name='live_network_monitor'),
    
    # Network join page for users
    path('network/<int:network_id>/join/', views_visual.network_join_view, name='network_join'),
    
    # List of available networks for monitoring/joining
    path('networks/', views_visual.live_networks_list, name='live_networks_list'),
    
    # API endpoints for AJAX polling
    path('api/network/<int:network_id>/status/', views_visual.get_network_status, name='api_network_status'),
    path('api/join-request/<int:request_id>/approve/', views_visual.approve_join_request_api, name='api_approve_join_request'),
    path('api/join-request/<int:request_id>/reject/', views_visual.reject_join_request_api, name='api_reject_join_request'),
]