# networks/views_admin.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import company_admin_required
from .models import Network, NetworkMembership, UnauthorizedAttempt
from .forms import NetworkForm
from alerts.models import IntruderLog
from django.http import HttpResponse
import csv

# 🔔 Notifications util
from notifications.utils import create_notification
from .models import JoinRequest  

@login_required
@company_admin_required
def company_networks(request):
    networks = Network.objects.filter(company=request.user.company).prefetch_related("memberships__user")
    return render(request, "networks/admin/company_networks.html", {"networks": networks})


@login_required
@company_admin_required
def create_network(request):
    if request.method == "POST":
        form = NetworkForm(request.POST)
        if form.is_valid():
            network = form.save(commit=False)
            network.company = request.user.company
            network.save()

            # Notify admins
            create_notification(
                request.user,
                f"Network '{network.name}' created successfully.",
                link="/admin/company-networks/"
            )

            return redirect("admin_company_networks")
    else:
        form = NetworkForm()
    return render(request, "networks/admin/network_form.html", {"form": form})


@login_required
@company_admin_required
def edit_network(request, network_id):
    network = get_object_or_404(Network, id=network_id, company=request.user.company)
    if request.method == "POST":
        form = NetworkForm(request.POST, instance=network)
        if form.is_valid():
            form.save()

            # Notify admins
            create_notification(
                request.user,
                f"Network '{network.name}' was updated.",
                link="/admin/company-networks/"
            )

            return redirect("admin_company_networks")
    else:
        form = NetworkForm(instance=network)
    return render(request, "networks/admin/network_form.html", {"form": form, "edit": True})


@login_required
@company_admin_required
def delete_network(request, network_id):
    network = get_object_or_404(Network, id=network_id, company=request.user.company)
    name = network.name
    network.delete()

    # Notify admins
    create_notification(
        request.user,
        f"Network '{name}' was deleted.",
        link="/admin/company-networks/"
    )

    return redirect("admin_company_networks")


@login_required
@company_admin_required
def unauthorized_attempts(request):
    attempts = UnauthorizedAttempt.objects.filter(
        network__company=request.user.company
    ).select_related("network", "user")
    return render(request, "networks/admin/unauthorized_attempts.html", {"attempts": attempts})


@login_required
@company_admin_required
def intruder_logs(request):
    logs = IntruderLog.objects.filter(status='unauthorized')

    # 🔔 Send notification when new intruder logs exist (optional: only latest one)
    if logs.exists():
        latest = logs.latest("timestamp")
        ua = latest.unauthorized_attempt
        create_notification(
            request.user,
            f"Intruder alert on network '{ua.network.name if ua else 'Unknown'}'.",
            link="/admin/intruder-logs/"
        )

    return render(request, "networks/admin/intruder_logs.html", {"logs": logs})


@login_required
@company_admin_required
def export_intruder_logs_csv(request):
    logs = IntruderLog.objects.filter(
        unauthorized_attempt__network__company=request.user.company
    )
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename=\"intruder_logs.csv\"'

    writer = csv.writer(response)
    writer.writerow(["MAC Address", "IP Address", "Status", "Timestamp", "Network", "Reason"])
    for log in logs:
        ua = log.unauthorized_attempt
        writer.writerow([
            log.mac_address,
            log.ip_address,
            log.status,
            log.timestamp,
            ua.network.name if ua else "N/A",
            ua.reason if ua else "N/A",
        ])

    return response


# ✅ Join Requests (Admin Approval)
@login_required
@company_admin_required
def join_requests(request):
    requests = JoinRequest.objects.filter(network__company=request.user.company, status="pending").select_related("user", "network")
    return render(request, "networks/admin/join_requests.html", {"requests": requests})


@login_required
@company_admin_required
def approve_join_request(request, request_id):
    jr = get_object_or_404(JoinRequest, id=request_id, network__company=request.user.company, status="pending")
    jr.status = "approved"
    jr.save()

    # Add user to network
    NetworkMembership.objects.get_or_create(user=jr.user, network=jr.network)

    # Notify employee
    create_notification(
        jr.user,
        f"Your request to join '{jr.network.name}' was approved.",
        link="/employee/my-networks/"
    )

    return redirect("admin_join_requests")


@login_required
@company_admin_required
def reject_join_request(request, request_id):
    jr = get_object_or_404(JoinRequest, id=request_id, network__company=request.user.company, status="pending")
    jr.status = "rejected"
    jr.save()

    # Notify employee
    create_notification(
        jr.user,
        f"Your request to join '{jr.network.name}' was rejected.",
        link="/employee/join-requests/"
    )

    return redirect("admin_join_requests")


from django.shortcuts import render
from .models import Network

@login_required
@company_admin_required
def live_networks_list(request):
    # Only show networks for the user's company
    networks = Network.objects.filter(company=request.user.company).order_by("name")
    return render(request, "networks/live/live_networks_list.html", {"networks": networks})
