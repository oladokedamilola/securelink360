# networks/urls.py
from django.urls import path
from . import views_discovery
from .views import *

urlpatterns = [
    path("directory/", views_discovery.network_directory, name="network_directory"),
    path("directory/request/<int:network_id>/", views_discovery.request_access, name="request_access"),
    path("directory/outsider/<int:network_id>/", views_discovery.outsider_attempt, name="outsider_attempt"),


    path('network/<uuid:network_id>/live/', network_live_view, name='network_live'),
    path('network/<uuid:network_id>/join/', network_join_view, name='network_join'),
]
