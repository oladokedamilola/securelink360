# networks/views_visual.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from accounts.decorators import company_admin_required, manager_required
from .models import Network, NetworkMembership

@login_required
def live_network(request, network_id):
    # Allow Admins or Managers of this network
    network = get_object_or_404(Network, id=network_id, company=request.user.company)
    is_member = NetworkMembership.objects.filter(network=network, user=request.user, active=True).exists()
    if not (is_member or request.user.is_company_admin()):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Not allowed")

    return render(request, "networks/live/live_network.html", {"network": network})
