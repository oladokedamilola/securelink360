from django.urls import path
from . import views_requests

urlpatterns = [
    # Admin
    path("admin/join-requests/", views_requests.company_join_requests, name="admin_company_join_requests"),
    path("admin/join-requests/<int:request_id>/<str:action>/", views_requests.handle_join_request_admin, name="admin_handle_join_request"),

    # Manager
    path("manager/join-requests/", views_requests.team_join_requests, name="manager_team_join_requests"),
    path("manager/join-requests/<int:request_id>/<str:action>/", views_requests.handle_join_request_manager, name="manager_handle_join_request"),
]
