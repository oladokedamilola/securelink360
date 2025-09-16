import random, uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from networks.models import Network
from alerts.models import IntruderLog

# Helper to generate fake network data
def _generate_fake_network_data(network_id):
    signal_strength = random.choice(["Strong", "Medium", "Weak"])
    types = ["Secured", "WPA2", "WPA3", "Enterprise"]
    description = random.choice([
        "Enterprise-grade secured Wi-Fi network.",
        "Corporate access point.",
        "Managed office hotspot.",
        "Secure company gateway."
    ])

    return {
        "id": network_id,
        "name": f"Corporate-WiFi-{network_id:03}",  # anonymized
        "signal": signal_strength,
        "type": random.choice(types),
        "description": description,
    }

# Legacy discovery page (public)
def discovery_page(request):
    networks = Network.objects.all().only("id")
    fake_networks = [_generate_fake_network_data(n.id) for n in networks]
    return render(request, "legacy/discovery.html", {"networks": fake_networks})

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from alerts.models import IntruderLog
from networks.models import NetworkMembership, Network
from notifications.utils import create_notification  # assuming you already have this

@csrf_exempt
def attempt_connect(request, network_id):
    """Handle intruder connection attempts on public discovery networks."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    ip = request.META.get("REMOTE_ADDR")
    ua = request.META.get("HTTP_USER_AGENT", "")

    # Create intruder log entry
    log = IntruderLog.objects.create(
        ip_address=ip,
        note=f"Public connection attempt on network {network_id}. UA={ua}",
        status="Detected",
        network_id=network_id  # 👈 ensure IntruderLog has a ForeignKey to Network
    )

    # Flash message (will show on next page load for logged-in admins)
    messages.warning(
        request,
        "🚨 Intruder detected! Their attempt was blocked automatically."
    )

    # Notify admins & managers of this network
    try:
        network = Network.objects.get(id=network_id)
        admins_managers = NetworkMembership.objects.filter(
            network=network,
            role__in=["admin", "manager"]
        ).select_related("user")

        for member in admins_managers:
            create_notification(
                member.user,
                f"🚨 Intruder detected on '{network.name}'. System blocked their attempt.",
                link="/n/admin/networks/unauthorized/"  # link to unauthorized attempts page    
            )
    except Network.DoesNotExist:
        pass  # safe guard if invalid network_id

    return JsonResponse({
        "status": "denied",
        "log_id": log.id,
        "message": "Intruder detected and blocked. Admins notified."
    })
