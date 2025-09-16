from django.urls import path
from . import views

urlpatterns = [
    path("mark-read/", views.mark_alerts_read, name="alerts-mark-read"),
]
