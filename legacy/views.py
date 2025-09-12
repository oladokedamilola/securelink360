import random, uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from networks.models import Network, UnauthorizedAttempt

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

# Intruder attempt handler
@csrf_exempt
def attempt_connect(request, network_id):
    if request.method == "POST":
        # Generate fake intruder MAC address
        fake_mac = ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
        ip_address = request.META.get("REMOTE_ADDR", "0.0.0.0")

        try:
            network = Network.objects.get(id=network_id)
        except Network.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Network not found"}, status=404)

        attempt = UnauthorizedAttempt.objects.create(
            network=network,
            user=None,
            ip_address=ip_address,
            mac_address=fake_mac,
            reason="Intruder attempted via legacy discovery page",
            created_at=now()
        )

        # Notification + IntruderLog handled in UnauthorizedAttempt.save()
        return JsonResponse({
            "status": "denied",
            "message": "Access Denied: Unauthorized device detected.",
            "mac": fake_mac,
            "ip": ip_address,
            "network": f"Corporate-WiFi-{network.id:03}",
        })

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
