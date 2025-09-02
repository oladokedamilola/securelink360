from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.decorators import company_admin_required, manager_required
from .models import JoinRequest, NetworkMembership, Network


# ---------------- ADMIN APPROVAL ---------------- #
@login_required
@company_admin_required
def company_join_requests(request):
    requests = JoinRequest.objects.filter(network__company=request.user.company).select_related("user", "network")
    return render(request, "networks/admin/company_join_requests.html", {"requests": requests})


@login_required
@company_admin_required
def handle_join_request_admin(request, request_id, action):
    join_request = get_object_or_404(JoinRequest, id=request_id, network__company=request.user.company)

    if action == "approve":
        join_request.status = "approved"
        join_request.decided_at = timezone.now()
        join_request.save()
        NetworkMembership.objects.get_or_create(
            network=join_request.network,
            user=join_request.user,
            defaults={"role": "employee"}
        )
    elif action == "deny":
        join_request.status = "denied"
        join_request.decided_at = timezone.now()
        join_request.save()

    return redirect("admin_company_join_requests")


# ---------------- MANAGER APPROVAL ---------------- #
@login_required
@manager_required
def team_join_requests(request):
    # Manager only sees requests in their networks
    manager_networks = Network.objects.filter(memberships__user=request.user, memberships__role="manager")
    requests = JoinRequest.objects.filter(network__in=manager_networks).select_related("user", "network")
    return render(request, "networks/manager/team_join_requests.html", {"requests": requests})


@login_required
@manager_required
def handle_join_request_manager(request, request_id, action):
    manager_networks = Network.objects.filter(memberships__user=request.user, memberships__role="manager")
    join_request = get_object_or_404(JoinRequest, id=request_id, network__in=manager_networks)

    if action == "approve":
        join_request.status = "approved"
        join_request.decided_at = timezone.now()
        join_request.save()
        NetworkMembership.objects.get_or_create(
            network=join_request.network,
            user=join_request.user,
            defaults={"role": "employee"}
        )
    elif action == "deny":
        join_request.status = "denied"
        join_request.decided_at = timezone.now()
        join_request.save()

    return redirect("manager_team_join_requests")
