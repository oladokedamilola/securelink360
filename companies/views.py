# companies/views.py
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



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CompanyProfileForm

@login_required
def company_profile(request):
    company = request.user.company
    if request.method == "POST":
        form = CompanyProfileForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Company profile updated successfully.")
            return redirect("admin_dashboard") 
    else:
        form = CompanyProfileForm(instance=company)

    return render(request, "companies/company_profile.html", {"form": form})




from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SecuritySettingForm
from .models import SecuritySetting

@login_required
def security_settings(request):
    company = request.user.company
    settings_instance, created = SecuritySetting.objects.get_or_create(company=company)

    if request.method == "POST":
        form = SecuritySettingForm(request.POST, instance=settings_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Security settings updated successfully.")
            return redirect("admin_dashboard")
    else:
        form = SecuritySettingForm(instance=settings_instance)

    return render(request, "companies/security_settings.html", {"form": form})
