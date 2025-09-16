# networks/views_manager.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import manager_required
from .models import Network, NetworkMembership
from alerts.models import IntruderLog
from .models import JoinRequest
from notifications.utils import create_notification


@login_required
@manager_required
def team_networks(request):
    memberships = NetworkMembership.objects.filter(user=request.user, role="manager")
    networks = Network.objects.filter(
        id__in=memberships.values("network_id")
    ).prefetch_related("memberships__user")

    return render(request, "networks/manager/team_networks.html", {"networks": networks})


@login_required
@manager_required
def team_unauthorized_attempts(request):
    networks = Network.objects.filter(
        memberships__user=request.user,
        memberships__role="manager"
    )
    attempts = IntruderLog.objects.filter(
        network__in=networks
    ).select_related("network", "user")

    # 🔔 Notify manager on suspicious unauthorized attempt
    if attempts.exists():
        latest = attempts.latest("timestamp")
        create_notification(
            request.user,
            f"Unauthorized attempt detected on '{latest.network.name}'.",
            link="/manager/team-unauthorized-attempts/"
        )

    return render(request, "networks/manager/team_unauthorized_attempts.html", {"attempts": attempts})


@login_required
@manager_required
def team_intruder_logs(request):
    networks = Network.objects.filter(
        memberships__user=request.user,
        memberships__role="manager"
    )
    logs = IntruderLog.objects.filter(
        unauthorized_attempt__network__in=networks
    ).select_related("unauthorized_attempt")

    # 🔔 Notify manager about latest intruder log
    if logs.exists():
        latest = logs.latest("timestamp")
        ua = latest.unauthorized_attempt
        create_notification(
            request.user,
            f"Intruder alert on your team network '{ua.network.name if ua else 'Unknown'}'.",
            link="/manager/team-intruder-logs/"
        )

    return render(request, "networks/manager/team_intruder_logs.html", {"logs": logs})


# ✅ Team Join Requests (Manager can only recommend/acknowledge, not finalize like Admin)
@login_required
@manager_required
def team_join_requests(request):
    networks = Network.objects.filter(
        memberships__user=request.user,
        memberships__role="manager"
    )
    requests = JoinRequest.objects.filter(
        network__in=networks,
        status="pending"
    ).select_related("user", "network")

    return render(request, "networks/manager/team_join_requests.html", {"requests": requests})


@login_required
@manager_required
def recommend_join_request(request, request_id):
    jr = get_object_or_404(
        JoinRequest,
        id=request_id,
        network__memberships__user=request.user,
        network__memberships__role="manager",
        status="pending"
    )
    jr.status = "recommended"   # not final approval
    jr.save()

    # 🔔 Notify admin(s) that manager has recommended
    create_notification(
        jr.network.company.admin,  # assuming company.admin points to admin user
        f"Manager {request.user.get_full_name()} recommended join request for '{jr.user.username}' on '{jr.network.name}'.",
        link="/admin/join-requests/"
    )

    # Notify employee
    create_notification(
        jr.user,
        f"Your request to join '{jr.network.name}' was recommended by your manager. Waiting for admin approval.",
        link="/employee/join-requests/"
    )

    return redirect("manager_team_join_requests")


@login_required
@manager_required
def reject_join_request_manager(request, request_id):
    jr = get_object_or_404(
        JoinRequest,
        id=request_id,
        network__memberships__user=request.user,
        network__memberships__role="manager",
        status="pending"
    )
    jr.status = "manager_rejected"
    jr.save()

    # Notify employee
    create_notification(
        jr.user,
        f"Your request to join '{jr.network.name}' was rejected by your manager.",
        link="/employee/join-requests/"
    )

    return redirect("manager_team_join_requests")
