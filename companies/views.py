from django.shortcuts import render
from devices.models import Device
from alerts.models import IntruderLog

def company_dashboard(request):
    company = request.user.company
    license_info = company.license
    devices = Device.objects.filter(company=company)
    alerts = IntruderLog.objects.filter(company=company)[:10]

    return render(request, "companies/dashboard.html", {
        "company": company,
        "license": license_info,
        "devices": devices,
        "alerts": alerts,
    })
