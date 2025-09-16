# # # networks/urls_admin.py
from django.urls import path
from . import views_admin

urlpatterns = [
    # Company Networks Management
    path("networks/", views_admin.company_networks, name="admin_company_networks"),
    path("networks/create/", views_admin.create_network, name="admin_create_network"),
    path("networks/<int:network_id>/edit/", views_admin.edit_network, name="admin_edit_network"),
    path("networks/<int:network_id>/delete/", views_admin.delete_network, name="admin_delete_network"),

    # Unauthorized Attempts
    path("networks/unauthorized/", views_admin.unauthorized_attempts, name="admin_unauthorized_attempts"),

    # Intruder Logs
    path("networks/intruder-logs/", views_admin.intruder_logs, name="admin_intruder_logs"),
    path("networks/intruder-logs/export/csv/", views_admin.export_intruder_logs_csv, name="export_intruder_logs_csv"),

    # Join Requests (Admin Approval)
    path("join-requests/", views_admin.join_requests, name="admin_join_requests"),
    path("join-requests/<int:request_id>/approve/", views_admin.approve_join_request, name="admin_approve_join_request"),
    path("join-requests/<int:request_id>/reject/", views_admin.reject_join_request, name="admin_reject_join_request"),
]






# from django.urls import path
# from . import views_admin
# from .views_visual import live_network


# urlpatterns = [
#     path('networks/<int:network_id>/live/', live_network, name='admin_live_network'),
#     path("live-networks/", views_admin.live_networks_list, name="live_networks_list"),
#     # Company Networks
#     path("admin/networks/", views_admin.company_networks, name="admin_company_networks"),
#     path("admin/networks/create/", views_admin.create_network, name="admin_create_network"),
#     path("admin/networks/<int:network_id>/edit/", views_admin.edit_network, name="admin_edit_network"),
#     path("admin/networks/<int:network_id>/delete/", views_admin.delete_network, name="admin_delete_network"),

#     # Unauthorized Attempts
#     path("admin/networks/unauthorized/", views_admin.unauthorized_attempts, name="admin_unauthorized_attempts"),

#     # Intruder Logs
#     path("admin/networks/intruder-logs/", views_admin.intruder_logs, name="admin_intruder_logs"),
#     path("admin/networks/intruder-logs/export/csv/", views_admin.export_intruder_logs_csv, name="export_intruder_logs_csv"),
# ]
