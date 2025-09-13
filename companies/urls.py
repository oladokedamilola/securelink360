from django.urls import path
from .views import *

urlpatterns = [
    path("dashboard/", company_dashboard, name="company_dashboard"),
    path("profile/", company_profile, name="company_profile"),
    path("security-settings/", security_settings, name="security_settings")
    
]
