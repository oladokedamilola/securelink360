from django.urls import path
from .views import company_dashboard

urlpatterns = [
    path("dashboard/", company_dashboard, name="company_dashboard"),
]
