# networks/urls_employee.py
from django.urls import path
from . import views_employee

urlpatterns = [
    path("my-networks/", views_employee.my_networks, name="employee_my_networks"),
    path("join-requests/", views_employee.join_requests, name="employee_join_requests"),
    path("join-requests/<int:request_id>/", views_employee.join_request_status, name="employee_join_request_status"),
    path("join-requests/<int:request_id>/cancel/", views_employee.cancel_join_request, name="employee_cancel_join_request"),
    # path("join-attempts-history/", views_employee.join_attempts_history, name="employee_join_attempts_history"),
]