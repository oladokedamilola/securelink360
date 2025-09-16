from django.shortcuts import render

# Home Page View
def home(request):
    return render(request, 'home.html')

# About Us Page View
def about(request):
    return render(request, 'about.html')

# Pricing Page View
def pricing(request):
    return render(request, 'pricing.html')

# Contact Us Page View
def contact(request):
    return render(request, 'contact.html')

# Privacy Policy Page View
def privacy_policy(request):
    return render(request, 'privacy_policy.html')



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import company_admin_required, manager_required
from companies.models import License, Announcement, Task
from devices.models import Device
from alerts.models import IntruderLog

# ----------------
# Admin Dashboard
# ----------------
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone

from accounts.decorators import company_admin_required
from devices.models import Device
from alerts.models import IntruderLog
from companies.models import Announcement, License, SecuritySetting
from networks.models import Network

@login_required
@company_admin_required
def admin_dashboard(request):
    user = request.user
    company = user.company

    # License info
    license = License.objects.filter(company=company).first()

    # Devices queryset + count
    devices = Device.objects.filter(user__company=company)
    devices_count = devices.count()

    # Alerts queryset + count (latest 4 alerts only)
    alerts = IntruderLog.objects.filter(
        network__company=company,
        status="Detected"
    ).order_by("-detected_at")[:4]
    alerts_count = alerts.count()

    # Recent announcements
    announcements = Announcement.objects.filter(company=company).order_by("-created_at")[:5]

    # Compute users_onboarded
    users_onboarded_qs = company.users.filter(
        (Q(first_name__isnull=False) & ~Q(first_name='')) | Q(devices__isnull=False)
    ).distinct()
    users_onboarded = users_onboarded_qs.count()

    # Onboarding checklist
    onboarding = {
        "company_profile": bool(company.name and getattr(company, "domain", None)),
        "invite_team": company.users.exclude(id=user.id).exists(),
        "add_device": devices_count > 0,
        "review_security": SecuritySetting.objects.filter(company=company).exists(),
        "create_network": Network.objects.filter(company=company).exists(),
        "users_onboarded": users_onboarded,
    }

    total_steps = len(onboarding)
    completed_steps = sum(1 for v in onboarding.values() if v)
    onboarding["percent_complete"] = int((completed_steps / total_steps) * 100) if total_steps else 100
    onboarding["complete"] = completed_steps == total_steps

    return render(request, "dashboards/admin_dashboard.html", {
        "user": user,
        "company": company,
        "license": license,
        "devices": devices,
        "devices_count": devices_count,
        "alerts": alerts,
        "alerts_count": alerts_count,
        "announcements": announcements,
        "onboarding": onboarding,
    })




# ----------------
# Manager Dashboard
# ----------------
@login_required
@manager_required
def manager_dashboard(request):
    user = request.user
    company = user.company

    # All employees (exclude other managers/admins)
    team_members = company.users.filter(role="employee")

    # Devices owned by employees
    team_devices = Device.objects.filter(user__in=team_members)

    # Intruder logs linked to these employees' devices OR company networks
    team_alerts = IntruderLog.objects.filter(
        Q(device__user__in=team_members) |
        Q(network__company=company),
        status="Detected"
    ).order_by("-detected_at")[:5]

    # Tasks assigned by this manager
    tasks = Task.objects.filter(assigned_by=user).order_by("-created_at")[:5]

    # Announcements scoped to this company or by this manager
    announcements = (Announcement.objects.filter(company=company) | Announcement.objects.filter(manager=user)).order_by("-created_at")[:5]

    # Onboarding progress
    profile_complete = bool(user.first_name and user.last_name and user.email)
    device_registered = user.devices.exists()
    mfa_enabled = getattr(user, "mfa_enabled", False)

    steps = [profile_complete, device_registered, mfa_enabled]
    percent_complete = int((sum(steps) / len(steps)) * 100)
    onboarding = {
        "profile_complete": profile_complete,
        "device_registered": device_registered,
        "mfa_enabled": mfa_enabled,
        "percent_complete": percent_complete,
        "complete": all(steps),
    }

    return render(request, "dashboards/manager_dashboard.html", {
        "team_members": team_members,
        "team_devices": team_devices,
        "team_alerts": team_alerts,
        "tasks": tasks,
        "announcements": announcements,
        "onboarding": onboarding,
    })




# ----------------
# Employee Dashboard
# ----------------
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from devices.models import Device
from companies.models import Announcement


@login_required
def employee_dashboard(request):
    user = request.user
    company = user.company

    # --- Tasks assigned to this employee ---
    tasks = Task.objects.filter(assigned_to=user).order_by("completed", "due_date")[:5]

    # --- Announcements (company + manager) ---
    announcements = Announcement.objects.filter(company=company, scope="company")
    if hasattr(user, "manager") and user.manager:
        announcements |= Announcement.objects.filter(manager=user.manager)
    announcements = announcements.distinct().order_by("-created_at")[:5]

    # --- Devices for this employee ---
    my_devices = Device.objects.filter(user=user)

    # --- Onboarding progress ---
    profile_complete = bool(user.first_name and user.last_name and user.email)
    device_registered = my_devices.exists()  # Use filtered devices for the employee
    mfa_enabled = getattr(user, "mfa_enabled", False)

    steps = [profile_complete, device_registered]
    percent_complete = int((sum(steps) / len(steps)) * 100)

    onboarding = {
        "profile_complete": profile_complete,
        "device_registered": device_registered,
        "mfa_enabled": mfa_enabled,
        "percent_complete": percent_complete,
        "complete": all(steps),
    }

    return render(request, "dashboards/employee_dashboard.html", {
        "tasks": tasks,
        "announcements": announcements,
        "my_devices": my_devices,
        "onboarding": onboarding,
    })







from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import company_admin_required
from companies.models import License, Announcement, Task
from accounts.models import User
from devices.models import Device
from alerts.models import IntruderLog
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import manager_required
from django.contrib import messages

@login_required
@company_admin_required
def admin_license(request):
    license = License.objects.filter(company=request.user.company).first()
    return render(request, "companies/admin/license.html", {"license": license})


@login_required
@company_admin_required
def admin_devices(request):
    devices = Device.objects.filter(user__company=request.user.company)
    return render(request, "companies/admin/devices.html", {"devices": devices})


@login_required
@company_admin_required
def block_device(request, device_id):
    device = get_object_or_404(Device, id=device_id, user__company=request.user.company)
    device.is_blocked = True
    device.save()
    messages.success(request, f"Device {device.name or device.mac_address} has been blocked.")
    return redirect("admin_devices")  # or your device management page


@login_required
@company_admin_required
def admin_alerts(request):
    alerts = IntruderLog.objects.filter(company=request.user.company).order_by("-timestamp")
    return render(request, "admin/alerts.html", {"alerts": alerts})

@login_required
@company_admin_required
def create_announcement(request):
    if request.method == "POST":
        Announcement.objects.create(
            manager=request.user,  # admin is still a "user"
            company=request.user.company,
            message=request.POST.get("message"),
            scope="company",
        )
        messages.success(request, "Company-wide announcement posted.")
        return redirect("announcements_list")
    return render(request, "companies/announcements/create_announcement.html")




#Manager Views
@login_required
@manager_required
def team_overview(request):
    team_members = User.objects.filter(manager=request.user)
    return render(request, "companies/managers/team_overview.html", {"team_members": team_members})

@login_required
@manager_required
def team_devices(request):
    devices = Device.objects.filter(user__manager=request.user)
    return render(request, "companies/managers/team_devices.html", {"devices": devices})

@login_required
@manager_required
def team_alerts(request):
    alerts = IntruderLog.objects.filter(device__user__manager=request.user).order_by("-timestamp")
    return render(request, "companies/managers/team_alerts.html", {"alerts": alerts})

@login_required
@manager_required
def team_announcements(request):
    team_members = User.objects.filter(manager=request.user)

    if request.method == "POST":
        if "announcement_submit" in request.POST:
            Announcement.objects.create(
                manager=request.user,
                message=request.POST.get("message"),
            )
        elif "task_submit" in request.POST:
            Task.objects.create(
                assigned_by=request.user,
                assigned_to_id=request.POST.get("assigned_to"),
                description=request.POST.get("description"),
                due_date=request.POST.get("due_date") or None,
            )
        return redirect("manager_team_announcements")

    announcements = Announcement.objects.filter(manager=request.user).order_by("-created_at")
    tasks = Task.objects.filter(assigned_by=request.user).order_by("-created_at")

    return render(
        request,
        "companies/managers/team_announcements.html",
        {"announcements": announcements, "tasks": tasks, "team_members": team_members},
    )




#Employee Views
@login_required
def employee_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user).order_by("completed", "due_date")
    return render(request, "companies/employee/employee_tasks.html", {"tasks": tasks})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    task.completed = True
    task.save()
    return redirect("employee_tasks")

from django.db import models

@login_required
def announcements_list(request):
    if request.user.role == "admin":
        announcements = Announcement.objects.filter(company=request.user.company)
    elif request.user.role == "manager":
        announcements = Announcement.objects.filter(
            models.Q(company=request.user.company, scope="company") |
            models.Q(manager=request.user)
        )
    else:  # employee
        # Only show company-wide announcements
        announcements = Announcement.objects.filter(
            company=request.user.company,
            scope="company"
        )

    announcements = announcements.order_by("-created_at")

    return render(request, "companies/announcements/announcements_list.html", {
        "announcements": announcements
    })


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from networks.models import Network, NetworkMembership
from alerts.models import IntruderLog
from django.shortcuts import get_object_or_404

@login_required
def mark_intruders_read(request):
    """Mark all intruders as read for the current admin."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    # You may pass network_id in the body if multiple networks exist
    network_id = request.POST.get("network_id") or request.GET.get("network_id")
    network = get_object_or_404(Network, id=network_id, company=request.user.company)

    # Permission check: only admin or manager can mark intruders
    membership = NetworkMembership.objects.filter(
        network=network,
        user=request.user,
        role__in=["admin", "manager"],
        active=True
    ).first()

    if not membership:
        return JsonResponse({"error": "Permission denied"}, status=403)

    # Update IntruderLog records to "Read" for this network
    IntruderLog.objects.filter(network=network, status="Detected").update(status="Read")

    return JsonResponse({"success": True, "message": "Intruder alerts marked as read."})
