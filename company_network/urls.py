from django.contrib import admin
from django.urls import path, include
from . import views
from accounts import views as account_views
urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('auth/', include('accounts.urls')),
    path('devices/', include('devices.urls')),
    path("company/", include("companies.urls")),
    path('alerts/', include('alerts.urls')),


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
    
    # Admin Pages
    path("admin/license/", views.admin_license, name="admin_license"),
    path("admin/devices/", views.admin_devices, name="admin_devices"),
    path("admin/alerts/", views.admin_alerts, name="admin_alerts"),

    path("admin/users/", account_views.user_management, name="user_management"),
    path("admin/users/invite/", account_views.send_invite, name="send_invite"),
    path("admin/users/<int:user_id>/edit/", account_views.edit_user, name="edit_user"),
    path("admin/users/<int:user_id>/deactivate/", account_views.deactivate_user, name="deactivate_user"),
    path("admin/invites/<uuid:invite_id>/resend/", account_views.resend_invite, name="resend_invite"),
    path("admin/invites/<uuid:invite_id>/revoke/", account_views.revoke_invite, name="revoke_invite"),
    path("invites/accept/<uuid:token>/", account_views.accept_invite, name="accept_invite"),


    # Manager Pages
    path("team/overview/", views.team_overview, name="manager_team_overview"),
    path("team/devices/", views.team_devices, name="manager_team_devices"),
    path("team/alerts/", views.team_alerts, name="manager_team_alerts"),
    path("team/announcements/", views.team_announcements, name="manager_team_announcements"),

    # employees/urls.py
    path("tasks/", views.employee_tasks, name="employee_tasks"),
    path("tasks/complete/<int:task_id>/", views.complete_task, name="complete_task"),



    path("announcements", views.announcements_list, name="announcements_list"),
    path("create/", views.create_announcement, name="create_announcement"),
]



# # project/urls.py
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from devices.views import DeviceViewSet

# router = DefaultRouter()
# router.register(r'devices', DeviceViewSet)

# urlpatterns = [
#     path('api/', include(router.urls)),
# ]