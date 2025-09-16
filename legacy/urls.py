# legacy/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("api/attempt-connect/<int:network_id>/", views.attempt_connect, name="attempt_connect"),
    
    path("discovery/", views.discovery_page, name="legacy_discovery"),
    path("attempt-connect/<int:network_id>/", views.attempt_connect, name="legacy_attempt_connect"),
]
# Legacy URLs for company network   
# Provides discovery page and intruder attempt handling
# Note: This module is for legacy support and should not be used in new implementations.