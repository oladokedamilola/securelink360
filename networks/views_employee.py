# networks/views_employee.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Network, NetworkMembership, JoinRequest, UnauthorizedAttempt
from notifications.utils import create_notification


@login_required
def my_networks(request):
    memberships = NetworkMembership.objects.filter(
        user=request.user
    ).select_related("network")

    return render(request, "networks/employee/my_networks.html", {
        "memberships": memberships
    })


@login_required
def join_requests(request):
    requests = JoinRequest.objects.filter(
        user=request.user
    ).select_related("network")

    available_networks = Network.objects.filter(
        company=request.user.company
    ).exclude(
        memberships__user=request.user
    ).exclude(
        join_requests__user=request.user
    )

    if request.method == "POST":
        network_id = request.POST.get("network_id")
        network = get_object_or_404(Network, id=network_id, company=request.user.company)

        jr = JoinRequest.objects.create(network=network, user=request.user)

        # 🔔 Notify manager(s) that an employee requested access
        managers = NetworkMembership.objects.filter(
            network=network, role="manager"
        ).select_related("user")

        for m in managers:
            create_notification(
                m.user,
                f"{request.user.get_full_name()} requested to join '{network.name}'.",
                link="/manager/team-join-requests/"
            )

        # 🔔 Notify employee (confirmation)
        create_notification(
            request.user,
            f"Your request to join '{network.name}' has been submitted and is pending manager/admin review.",
            link="/employee/join-requests/"
        )

        return redirect("employee_join_requests")

    return render(request, "networks/employee/join_requests.html", {
        "requests": requests,
        "available_networks": available_networks,
    })


@login_required
def join_attempts_history(request):
    attempts = UnauthorizedAttempt.objects.filter(
        user=request.user
    ).select_related("network")

    return render(request, "networks/employee/join_attempts_history.html", {
        "attempts": attempts
    })


# ✅ Extra helper to display status updates clearly (recommended/rejected/approved)
@login_required
def join_request_status(request, request_id):
    jr = get_object_or_404(JoinRequest, id=request_id, user=request.user)

    # 🔔 When employee views, they see latest status update
    if jr.status in ["approved", "manager_rejected", "admin_rejected", "recommended"]:
        create_notification(
            request.user,
            f"Update on your request to join '{jr.network.name}': {jr.get_status_display()}",
            link="/employee/join-requests/"
        )

    return render(request, "networks/employee/join_request_status.html", {"request_obj": jr})
