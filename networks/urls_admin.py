from django.urls import path
from . import views_admin

urlpatterns = [
    # Company Networks
    path("admin/networks/", views_admin.company_networks, name="admin_company_networks"),
    path("admin/networks/create/", views_admin.create_network, name="admin_create_network"),
    path("admin/networks/<int:network_id>/edit/", views_admin.edit_network, name="admin_edit_network"),
    path("admin/networks/<int:network_id>/delete/", views_admin.delete_network, name="admin_delete_network"),

    # Unauthorized Attempts
    path("admin/networks/unauthorized/", views_admin.unauthorized_attempts, name="admin_unauthorized_attempts"),

    # Intruder Logs
    path("admin/networks/intruder-logs/", views_admin.intruder_logs, name="admin_intruder_logs"),
    path("admin/networks/intruder-logs/export/csv/", views_admin.export_intruder_logs_csv, name="export_intruder_logs_csv"),
]
