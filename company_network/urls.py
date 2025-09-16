from django.contrib import admin
from django.urls import path, include
from . import views
from accounts import views as account_views
from alerts import views as alerts_views
from notifications.views import my_notifications
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('auth/', include('accounts.urls')),
    path('devices/', include('devices.urls')),
    path("company/", include("companies.urls")),
    path('alerts/', include('alerts.urls')),
    path('l/', include('legacy.urls')),
    path('legacy/', include('legacy.urls')),
    # networks/urls_admin.py -> for admin
    path("n/admin/", include("networks.urls_admin")),

    # networks/urls_manager.py -> for manager
    path("n/manager/", include("networks.urls_manager")),

    # networks/urls_employee.py -> for employee
    path("n/employee/", include("networks.urls_employee")),

    # networks/urls_visual.py -> live networks
    path('n/live/', include('networks.urls_visual')),  # For HTTP route
    path('n/live/api/mark-intruders-read/', views.mark_intruders_read, name='mark_intruders_read'),
    path("requests/", include("networks.urls_requests")),  # join requests


    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('pricing/', views.pricing, name='pricing'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    # path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    # path('dashboard/', views.dashboard, name='dashboard'),
    # path('profile/', views.profile, name='profile'),
    # path('settings/', views.settings, name='settings'),
    # path('reports/', views.reports, name='reports'),
    
    # --- Admin Dashboard Pages ---
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/dashboard/license/", views.admin_license, name="admin_license"),
    path("admin/dashboard/devices/", views.admin_devices, name="admin_devices"),
    path("admin/dashboard/devices/<int:device_id>/block/", views.block_device, name="block_device"),
    path("admin/dashboard/alerts/", views.admin_alerts, name="admin_alerts"),
    path("admin/dashboard/users/", account_views.user_management, name="user_management"),
    path("admin/dashboard/invite/", account_views.send_invite, name="send_invite"),
    path("admin/dashboard/users/<int:user_id>/edit/", account_views.edit_user, name="edit_user"),
    path("admin/dashboard/users/<int:user_id>/deactivate/", account_views.deactivate_user, name="deactivate_user"),
    
    path("admin/dashboard/invite/<int:invite_id>/resend/", account_views.resend_invite, name="resend_invite"),
    path("admin/dashboard/invite/<int:invite_id>/revoke/", account_views.revoke_invite, name="revoke_invite"),
    path("invites/accept/<uuid:token>/", account_views.accept_invite, name="accept_invite"),
    
    path("create/", views.create_announcement, name="create_announcement"),
    path("alerts/", alerts_views.alert_list, name="alert_list"),
    
    # Manager Pages
    path("team/overview/", views.team_overview, name="manager_team_overview"),
    path("team/devices/", views.team_devices, name="manager_team_devices"),
    path("team/alerts/", views.team_alerts, name="manager_team_alerts"),
    path("team/announcements/", views.team_announcements, name="manager_team_announcements"),

    # Employee Pages
    path("tasks/", views.employee_tasks, name="employee_tasks"),
    path("tasks/complete/<int:task_id>/", views.complete_task, name="complete_task"),


    # General
    path("announcements/", views.announcements_list, name="announcements_list"),
    path('notifications/', my_notifications, name='my_notifications'),


    # Dashboards
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/manager/", views.manager_dashboard, name="manager_dashboard"),
    path("dashboard/employee/", views.employee_dashboard, name="employee_dashboard"),



    path('admin/', admin.site.urls),
]

# Serve media files only in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# # project/urls.py
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from devices.views import DeviceViewSet

# router = DefaultRouter()
# router.register(r'devices', DeviceViewSet)

# urlpatterns = [
#     path('api/', include(router.urls)),
# ]