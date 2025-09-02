from django.urls import path
from . import views_manager

urlpatterns = [
    path("team/networks/", views_manager.team_networks, name="manager_team_networks"),
    path("team/unauthorized-attempts/", views_manager.team_unauthorized_attempts, name="manager_team_unauthorized_attempts"),
    path("team/intruder-logs/", views_manager.team_intruder_logs, name="manager_team_intruder_logs"),
]
