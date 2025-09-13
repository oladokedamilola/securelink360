from django.shortcuts import render
from .models import IntruderLog

def alert_list(request):
    alerts = IntruderLog.objects.filter(device__company=request.user.company).order_by("-detected_at")
    return render(request, "alerts/alert_list.html", {"alerts": alerts})
