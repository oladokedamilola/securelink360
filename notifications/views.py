# notifications/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def my_notifications(request):
    notifications = request.user.notifications.order_by("-created_at")
    return render(request, "notifications/my_notifications.html", {"notifications": notifications})
