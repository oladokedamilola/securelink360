from django.urls import path
from . import views_employee

urlpatterns = [
    path("my-networks/", views_employee.my_networks, name="employee_my_networks"),
    path("join-requests/", views_employee.join_requests, name="employee_join_requests"),
    path("join-attempts-history/", views_employee.join_attempts_history, name="employee_join_attempts_history"),
]
