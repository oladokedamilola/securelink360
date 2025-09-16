# networks/views_admin.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import company_admin_required
from .models import Network, NetworkMembership
from .forms import NetworkForm
from alerts.models import IntruderLog
from django.http import HttpResponse
import csv
from django.utils import timezone
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
    attempts = IntruderLog.objects.filter(
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
    # Pending requests with all related data
    pending_requests = JoinRequest.objects.filter(
        network__company=request.user.company, 
        status="pending"
    ).select_related("user", "network", "device")
    
    # Recently processed requests (last 10)
    processed_requests = JoinRequest.objects.filter(
        network__company=request.user.company,
        status__in=["approved", "rejected"]
    ).select_related("user", "network", "device", "decided_by").order_by("-decided_at")[:10]
    
    return render(request, "networks/admin/join_requests.html", {
        "requests": pending_requests,
        "processed_requests": processed_requests
    })


@login_required
@company_admin_required
def approve_join_request(request, request_id):
    jr = get_object_or_404(JoinRequest, id=request_id, network__company=request.user.company, status="pending")
    jr.status = "approved"
    jr.decided_by = request.user
    jr.decided_at = timezone.now()
    jr.save()

    # Add user to network - MAKE SURE THIS IS WORKING
    membership, created = NetworkMembership.objects.get_or_create(
        user=jr.user, 
        network=jr.network,
        defaults={
            "role": "employee", 
            "active": True,
            "joined_at": timezone.now()
        }
    )
    
    print(f"DEBUG: Created membership for {jr.user.email} in {jr.network.name}. Created: {created}")  # Debug line

    # Update device status if a device was specified
    if jr.device:
        jr.device.status = "online"
        jr.device.save()

    # Notify employee
    create_notification(
        jr.user,
        f"Your request to join '{jr.network.name}' was approved. You are now connected!",
        link="/n/employee/my-networks/"
    )

    return redirect("admin_join_requests")


@login_required
@company_admin_required
def reject_join_request(request, request_id):
    jr = get_object_or_404(JoinRequest, id=request_id, network__company=request.user.company, status="pending")
    jr.status = "rejected"
    jr.decided_by = request.user  # Set who made the decision
    jr.decided_at = timezone.now()
    jr.save()

    # Update device status back to offline if a device was specified
    if jr.device:
        jr.device.status = "offline"
        jr.device.save()

    # Notify employee
    create_notification(
        jr.user,
        f"Your request to join '{jr.network.name}' was rejected.",
        link="/employee/join-requests/"
    )

    # Notify admin about the rejection
    create_notification(
        request.user,
        f"Rejected join request from {jr.user.email} for network '{jr.network.name}'.",
        link="/n/admin/join-requests/"
    )

    return redirect("admin_join_requests")


from django.shortcuts import render
from .models import Network

@login_required
def live_networks_list(request):
    # Only show networks for the user's company
    networks = Network.objects.filter(company=request.user.company).order_by("name")
    return render(request, "networks/live/live_networks_list.html", {"networks": networks})
