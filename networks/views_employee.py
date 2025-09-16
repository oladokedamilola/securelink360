# networks/views_employee.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Network, NetworkMembership, JoinRequest
from notifications.utils import create_notification
from devices.models import Device

@login_required
def my_networks(request):
    """Show networks the employee is currently a member of"""
    memberships = NetworkMembership.objects.filter(
        user=request.user
    ).select_related("network")

    return render(request, "networks/employee/my_networks.html", {
        "memberships": memberships
    })


@login_required
def join_requests(request):
    """Show employee's join requests and allow them to make new requests"""
    # Get all join requests for this user
    requests = JoinRequest.objects.filter(
        user=request.user
    ).select_related("network").order_by("-created_at")

    # Get networks the user can join (not already a member and not already requested)
    user_network_ids = NetworkMembership.objects.filter(
        user=request.user
    ).values_list('network_id', flat=True)

    user_requested_network_ids = JoinRequest.objects.filter(
        user=request.user,
        status="pending"
    ).values_list('network_id', flat=True)

    available_networks = Network.objects.filter(
        company=request.user.company,
        visibility__in=['company', 'public']
    ).exclude(id__in=user_network_ids).exclude(id__in=user_requested_network_ids)

    if request.method == "POST":
        network_id = request.POST.get("network_id")
        device_id = request.POST.get("device_id")
        
        network = get_object_or_404(Network, id=network_id, company=request.user.company)
        
        # Validate device belongs to user
        device = None
        if device_id:
            device = get_object_or_404(Device, id=device_id, user=request.user)
            # Update device status to pending
            device.status = "pending"
            device.save()

        # Create join request
        jr = JoinRequest.objects.create(
            network=network, 
            user=request.user,
            device=device,
            ip_address=get_client_ip(request)
        )

        # Notify network admins and managers
        admins_managers = NetworkMembership.objects.filter(
            network=network,
            role__in=["admin", "manager"]
        ).select_related("user")

        for member in admins_managers:
            create_notification(
                member.user,
                f"{request.user.get_full_name()} requested to join '{network.name}'.",
                link="/n/admin/join-requests/"
            )

        # Notify employee
        create_notification(
            request.user,
            f"Your request to join '{network.name}' has been submitted for review.",
            link="/n/employee/join-requests/"
        )

        return redirect("employee_join_requests")

    # Get user's devices for the join form
    user_devices = Device.objects.filter(user=request.user, is_blocked=False)

    return render(request, "networks/employee/join_requests.html", {
        "requests": requests,
        "available_networks": available_networks,
        "user_devices": user_devices,
    })


# @login_required
# def join_attempts_history(request):
#     """Show history of join attempts (including unauthorized attempts)"""
#     # Get successful join requests
#     join_requests = JoinRequest.objects.filter(
#         user=request.user
#     ).select_related("network").order_by("-created_at")

#     # Get unauthorized attempts
#     unauthorized_attempts = UnauthorizedAttempt.objects.filter(
#         user=request.user
#     ).select_related("network").order_by("-timestamp")

#     return render(request, "networks/employee/join_attempts_history.html", {
#         "join_requests": join_requests,
#         "unauthorized_attempts": unauthorized_attempts,
#     })


@login_required
def join_request_status(request, request_id):
    """Show detailed status of a specific join request"""
    jr = get_object_or_404(JoinRequest, id=request_id, user=request.user)

    # Mark notification as read when viewing status
    if jr.status in ["approved", "rejected"]:
        create_notification(
            request.user,
            f"Update: Your request to join '{jr.network.name}' was {jr.status}.",
            link=f"/n/employee/join-request/{jr.id}/"
        )

    return render(request, "networks/employee/join_request_status.html", {
        "request_obj": jr
    })


@login_required
def cancel_join_request(request, request_id):
    """Allow employees to cancel their pending join requests"""
    jr = get_object_or_404(JoinRequest, id=request_id, user=request.user, status="pending")
    
    if request.method == "POST":
        # Update device status back to offline if a device was specified
        if jr.device:
            jr.device.status = "offline"
            jr.device.save()
        
        jr.status = "cancelled"
        jr.save()
        
        # Notify admins/managers
        admins_managers = NetworkMembership.objects.filter(
            network=jr.network,
            role__in=["admin", "manager"]
        ).select_related("user")

        for member in admins_managers:
            create_notification(
                member.user,
                f"{request.user.get_full_name()} cancelled their join request for '{jr.network.name}'.",
                link="/n/admin/join-requests/"
            )

        # Notify employee
        create_notification(
            request.user,
            f"Your join request for '{jr.network.name}' has been cancelled.",
            link="/n/employee/join-requests/"
        )

        return redirect("employee_join_requests")
    
    return render(request, "networks/employee/cancel_join_request.html", {
        "request_obj": jr
    })


# Helper function to get client IP
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip