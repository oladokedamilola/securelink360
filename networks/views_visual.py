# networks/views_visual.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from accounts.decorators import company_admin_required
from .models import Network, NetworkMembership
from alerts.models import IntruderLog


@login_required
@company_admin_required
def live_network(request, network_id):
    """
    Render the live network page for admins/managers.
    """
    network = get_object_or_404(Network, id=network_id, company=request.user.company)

    # Ensure current user is marked as active in this network
    membership, created = NetworkMembership.objects.get_or_create(
        network=network,
        user=request.user,
        defaults={"active": True, "role": "admin"}
    )
    if not membership.active:
        membership.active = True
        membership.save()

    # ✅ Get only active devices for users who are members of this network
    active_devices = Device.objects.filter(
        user__network_memberships__network=network,
        user__network_memberships__active=True,
        status="online",           # only currently online
        is_blocked=False           # ignore blocked devices
    ).select_related("user").distinct()

    return render(
        request,
        "networks/live/live_network.html",
        {"network": network, "active_devices": active_devices}
    )


# networks/views_visual.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Network, NetworkMembership, JoinRequest
from devices.models import Device

@login_required
def live_networks_list(request):
    """
    Show list of networks that the user can monitor or join based on their role.
    Employees see ALL company networks, but each card shows whether the user
    is already a member, has a pending/approved/denied join request, or can join.
    """
    user = request.user
    networks = Network.objects.filter(company=user.company).order_by("name")

    # ---- Admin view ----
    if user.role == "admin":
        return render(request, "networks/live/live_networks_list.html", {
            "networks": networks,
            "user_role": "admin"
        })

    # ---- Manager view ----
    if user.role == "manager":
        user_admin_networks = Network.objects.filter(
            company=user.company,
            memberships__user=user,
            memberships__role='admin'
        )
        return render(request, "networks/live/live_networks_list.html", {
            "networks": networks,
            "user_admin_networks": user_admin_networks,
            "user_role": "manager"
        })

    # ---- Employee view ----
    # Show ALL company networks, but annotate each with membership/request info.
    # Efficiently fetch membership and join request info for the current user.
    member_qs = NetworkMembership.objects.filter(user=user).values('network_id', 'role')
    member_ids = set()
    membership_roles = {}
    for m in member_qs:
        nid = m['network_id']
        member_ids.add(nid)
        membership_roles[nid] = m['role']

    join_qs = JoinRequest.objects.filter(user=user, network__in=networks).select_related('network', 'device')
    join_map = {jr.network_id: jr for jr in join_qs}

    networks_with_status = []
    for net in networks:
        nid = net.id
        networks_with_status.append({
            "network": net,
            "is_member": nid in member_ids,
            "membership_role": membership_roles.get(nid),
            "join_request": join_map.get(nid)  # None if no request
        })

    return render(request, "networks/live/live_networks_list.html", {
        "networks_with_status": networks_with_status,
        "user_role": "employee"
    })
    
    
@login_required
def live_network(request, network_id):
    """
    Render the live network monitoring dashboard
    """
    network = get_object_or_404(Network, id=network_id)
    user = request.user
    
    # Check permissions
    if user.is_company_admin:
        # Admins can monitor any network in their company
        if network.company != user.company:
            return HttpResponseForbidden("You can only monitor networks in your company.")
    
    elif user.role == "manager":
        # Managers can monitor networks they admin
        try:
            membership = NetworkMembership.objects.get(network=network, user=user)
            if membership.role != 'admin':
                return HttpResponseForbidden("You must be an admin of this network to monitor it.")
        except NetworkMembership.DoesNotExist:
            return HttpResponseForbidden("You are not a member of this network.")
    
    else:
        # Employees cannot monitor networks
        return HttpResponseForbidden("Only admins and managers can monitor networks.")
    
    # Ensure user is marked as active in this network
    membership, created = NetworkMembership.objects.get_or_create(
        network=network,
        user=user,
        defaults={"active": True, "role": "admin" if user.is_company_admin else "manager"}
    )
    if not membership.active:
        membership.active = True
        membership.save()
    
    return render(request, "networks/live/live_network.html", {
        "network": network,
        "user_role": "admin" if user.is_company_admin else "manager"
    })

@login_required
def network_join_view(request, network_id):
    """
    Page for users to request to join a network
    """
    network = get_object_or_404(Network, id=network_id)
    user = request.user
    
    # Check if user is already a member
    if NetworkMembership.objects.filter(network=network, user=user).exists():
        return render(request, "networks/live/already_member.html", {
            "network": network
        })
    
    # Check if user can join this network
    if network.company != user.company and network.visibility != 'public':
        return HttpResponseForbidden("You cannot join this network.")
    
    # Get user's devices
    user_devices = Device.objects.filter(user=user, is_blocked=False)
    
    # Check for existing pending request
    existing_request = JoinRequest.objects.filter(
        network=network, 
        user=user, 
        status="pending"
    ).first()
    
    return render(request, "networks/live/network_join.html", {
        "network": network,
        "user_devices": user_devices,
        "existing_request": existing_request
    })



# networks/views_visual.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from devices.models import Device
from .models import Network, NetworkMembership, JoinRequest


from django.utils import timezone
from datetime import timedelta

from django.contrib import messages

@login_required
def get_network_status(request, network_id):
    """API endpoint to get current network status for AJAX polling"""
    network = get_object_or_404(Network, id=network_id, company=request.user.company)

    # 🔒 Permission check
    if not request.user.is_company_admin:
        try:
            membership = NetworkMembership.objects.get(network=network, user=request.user)
            if membership.role != "admin":
                return JsonResponse({"error": "Permission denied"}, status=403)
        except NetworkMembership.DoesNotExist:
            return JsonResponse({"error": "Permission denied"}, status=403)

    # ✅ Active, online, not-blocked devices
    devices = (
        Device.objects.filter(
            user__network_memberships__network=network,
            user__network_memberships__active=True,
            status="online",
            is_blocked=False,
        )
        .select_related("user")
        .distinct()
    )

    # ✅ Pending join requests
    pending_requests = (
        JoinRequest.objects.filter(network=network, status="pending")
        .select_related("user", "device")
    )

    # ✅ Active intruders (last 1 minute only)
    intruders_qs = IntruderLog.objects.filter(
        network=network,
        status="Detected",
        detected_at__gte=timezone.now() - timedelta(minutes=1)
    )

    intruders = [
        {
            "id": log.id,
            "status": "intruder",
            "ip_address": log.ip_address,
            "mac_address": log.mac_address or "",
            "detected_at": log.detected_at.isoformat(),
            "note": log.note,
        }
        for log in intruders_qs
    ]

    # 🚨 Add flash-style message if intruders exist
    flash_message = None
    if intruders_qs.exists():
        flash_message = "🚨 Intruder detected! Their attempt was blocked."

    return JsonResponse(
        {
            "devices": [
                {
                    "id": device.id,
                    "name": device.name,
                    "mac_address": device.mac_address,
                    "status": device.status,
                    "user_email": device.user.email if device.user else "Unassigned",
                    "ip_address": device.ip_address,
                }
                for device in devices
            ],
            "pending_requests": [
                {
                    "id": req.id,
                    "user_email": req.user.email,
                    "device_name": req.device.name if req.device else "No device",
                    "device_mac": req.device.mac_address if req.device else "",
                    "ip_address": req.ip_address,
                    "created_at": req.created_at.isoformat(),
                    "status": req.status,
                }
                for req in pending_requests
            ],
            "intruders": intruders,
            "flash_message": flash_message,  # 👈 frontend can show this like a toast
            "network": {
                "id": network.id,
                "name": network.name,
                "description": network.description,
                "visibility": network.visibility,
                "member_count": network.memberships.filter(active=True).count(),
            },
        }
    )



@login_required
@require_POST
@csrf_exempt
def approve_join_request_api(request, request_id):
    """API endpoint to approve a join request"""
    jr = get_object_or_404(
        JoinRequest, id=request_id, network__company=request.user.company
    )

    if jr.status != "pending":
        return JsonResponse({"error": "Request already processed"}, status=400)

    jr.status = "approved"
    jr.decided_by = request.user
    jr.save()

    # Add user to network if not already a member
    NetworkMembership.objects.get_or_create(
        user=jr.user,
        network=jr.network,
        defaults={"role": "employee", "active": True},
    )

    # Update device status
    if jr.device:
        jr.device.status = "online"
        jr.device.is_blocked = False
        jr.device.save()

    return JsonResponse({"success": True, "message": "Request approved"})


@login_required
@require_POST
@csrf_exempt
def reject_join_request_api(request, request_id):
    """API endpoint to reject a join request"""
    jr = get_object_or_404(
        JoinRequest, id=request_id, network__company=request.user.company
    )

    if jr.status != "pending":
        return JsonResponse({"error": "Request already processed"}, status=400)

    jr.status = "rejected"
    jr.decided_by = request.user
    jr.save()

    # Update device status back to offline (or blocked if you prefer)
    if jr.device:
        jr.device.status = "offline"
        jr.device.save()

    return JsonResponse({"success": True, "message": "Request rejected"})
