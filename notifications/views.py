# notifications/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def my_notifications(request):
    # Fetch notifications ordered by newest first
    notifications = request.user.notifications.order_by("-created_at")

    # Mark all unread notifications as read immediately when page is viewed
    notifications.filter(read=False).update(read=True)

    return render(request, "notifications/my_notifications.html", {"notifications": notifications})