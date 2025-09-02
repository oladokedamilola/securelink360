# networks/views_discovery.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Network, JoinRequest, UnauthorizedAttempt
from alerts.models import IntruderLog
from notifications.utils import create_notification

@login_required
def network_directory(request):
    query = request.GET.get("q", "")
    company = request.user.company

    networks = Network.objects.filter(company=company)
    if query:
        networks = networks.filter(Q(name__icontains=query))

    memberships = request.user.networkmembership_set.values_list("network_id", flat=True)
    pending_requests = request.user.joinrequest_set.values_list("network_id", flat=True)

    return render(request, "networks/discovery/network_directory.html", {
        "networks": networks,
        "memberships": memberships,
        "pending_requests": pending_requests,
        "query": query,
    })


@login_required
def request_access(request, network_id):
    network = get_object_or_404(Network, id=network_id, company=request.user.company)

    # prevent duplicates
    if not JoinRequest.objects.filter(user=request.user, network=network).exists():
        jr = JoinRequest.objects.create(user=request.user, network=network)

        # 🔔 notify managers/admins
        managers = network.memberships.filter(role="manager").select_related("user")
        for m in managers:
            create_notification(
                m.user,
                f"{request.user.get_full_name()} requested to join '{network.name}'.",
                link="/manager/team-join-requests/"
            )

        admins = request.user.company.admins.all()  # assuming related name
        for a in admins:
            create_notification(
                a,
                f"{request.user.get_full_name()} requested to join '{network.name}'.",
                link="/admin/join-requests/"
            )

        # confirm to employee
        create_notification(
            request.user,
            f"Your request to join '{network.name}' has been submitted.",
            link="/employee/join-requests/"
        )

    return redirect("network_directory")


def outsider_attempt(request, network_id):
    """
    Simulate outsider hitting discovery endpoint (not logged in or wrong company).
    """
    if not request.user.is_authenticated or not hasattr(request.user, "company"):
        network = get_object_or_404(Network, id=network_id)

        ua = UnauthorizedAttempt.objects.create(
            network=network,
            reason="Outsider attempted access to network directory"
        )
        IntruderLog.objects.create(
            unauthorized_attempt=ua,
            mac_address="??:??:??:??:??:??",  # later captured from request meta
            ip_address=request.META.get("REMOTE_ADDR"),
            status="blocked"
        )

        # 🔔 notify admins in real-time
        admins = network.company.admins.all()
        for a in admins:
            create_notification(
                a,
                f"⚠️ Intruder attempt detected on '{network.name}'.",
                link="/admin/intruder-logs/"
            )

    return redirect("home")
