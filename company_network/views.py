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
@login_required
@company_admin_required
def admin_dashboard(request):
    license = License.objects.filter(company=request.user.company).first()
    devices_count = Device.objects.filter(company=request.user.company).count()
    alerts_count = IntruderLog.objects.filter(company=request.user.company).count()
    announcements = Announcement.objects.filter(company=request.user.company).order_by("-created_at")[:5]

    return render(request, "dashboards/admin_dashboard.html", {
        "license": license,
        "devices_count": devices_count,
        "alerts_count": alerts_count,
        "announcements": announcements,
    })


# ----------------
# Manager Dashboard
# ----------------
@login_required
@manager_required
def manager_dashboard(request):
    team_members = request.user.users.all()  # Users linked to the same company that this manager manages
    team_devices = Device.objects.filter(user__in=team_members)
    team_alerts = IntruderLog.objects.filter(device__user__in=team_members).order_by("-timestamp")[:5]
    tasks = Task.objects.filter(assigned_by=request.user).order_by("-created_at")[:5]
    announcements = Announcement.objects.filter(manager=request.user).order_by("-created_at")[:5]

    return render(request, "dashboards/manager_dashboard.html", {
        "team_members": team_members,
        "team_devices_count": team_devices.count(),
        "team_alerts": team_alerts,
        "tasks": tasks,
        "announcements": announcements,
    })


# ----------------
# Employee Dashboard
# ----------------
@login_required
def employee_dashboard(request):
    tasks = Task.objects.filter(assigned_to=request.user).order_by("completed", "due_date")[:5]
    announcements = Announcement.objects.filter(
        company=request.user.company, scope="company"
    ) | Announcement.objects.filter(manager=request.user.manager)

    return render(request, "dashboards/employee_dashboard.html", {
        "tasks": tasks,
        "announcements": announcements.order_by("-created_at")[:5],
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
    return render(request, "admin/license.html", {"license": license})


@login_required
@company_admin_required
def admin_devices(request):
    devices = Device.objects.filter(company=request.user.company)
    return render(request, "admin/devices.html", {"devices": devices})


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
    return render(request, "announcements/create_announcement.html")




#Manager Views
@login_required
@manager_required
def team_overview(request):
    team_members = User.objects.filter(manager=request.user)
    return render(request, "managers/team_overview.html", {"team_members": team_members})

@login_required
@manager_required
def team_devices(request):
    devices = Device.objects.filter(user__manager=request.user)
    return render(request, "managers/team_devices.html", {"devices": devices})

@login_required
@manager_required
def team_alerts(request):
    alerts = IntruderLog.objects.filter(device__user__manager=request.user).order_by("-timestamp")
    return render(request, "managers/team_alerts.html", {"alerts": alerts})

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
        "managers/team_announcements.html",
        {"announcements": announcements, "tasks": tasks, "team_members": team_members},
    )




#Employee Views
@login_required
def employee_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user).order_by("completed", "due_date")
    return render(request, "employees/employee_tasks.html", {"tasks": tasks})

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
            models.Q(company=request.user.company, scope="company")
            | models.Q(manager=request.user)
        )
    else:  # employee
        announcements = Announcement.objects.filter(
            models.Q(company=request.user.company, scope="company")
            | models.Q(manager=request.user.manager)
        )

    announcements = announcements.order_by("-created_at")

    return render(request, "announcements/announcements_list.html", {
        "announcements": announcements
    })
