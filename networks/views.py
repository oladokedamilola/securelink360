# networks/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Network, NetworkMembership
from devices.models import Device
from django.http import HttpResponseForbidden


@login_required
def network_live_view(request, network_id):
    network = get_object_or_404(Network, id=network_id)
    
    # Check if user is admin of this network
    membership = get_object_or_404(NetworkMembership, network=network, user=request.user)
    if membership.role != 'admin':
        return HttpResponseForbidden("You must be a network administrator to view this page.")
    
    return render(request, 'networks/network_live.html', {
        'network': network
    })

@login_required
def network_join_view(request, network_id):
    network = get_object_or_404(Network, id=network_id)
    user_devices = Device.objects.filter(user=request.user, is_blocked=False)
    
    return render(request, 'networks/network_join.html', {
        'network': network,
        'user_devices': user_devices
    })