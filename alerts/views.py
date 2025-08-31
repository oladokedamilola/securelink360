from django.shortcuts import render
from .models import IntruderLog

def alert_list(request):
    alerts = IntruderLog.objects.filter(company=request.user.company)
    return render(request, "alerts/alert_list.html", {"alerts": alerts})
