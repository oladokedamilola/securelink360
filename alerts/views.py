from django.shortcuts import render
from .models import IntruderLog

def alert_list(request):
    alerts = IntruderLog.objects.filter(device__company=request.user.company).order_by("-detected_at")
    return render(request, "alerts/alert_list.html", {"alerts": alerts})


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from notifications.models import Notification  

@login_required
@require_POST
def mark_alerts_read(request):
    """Mark all current user's alerts as read."""
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return JsonResponse({"status": "ok"})
