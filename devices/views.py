# devices/views.py
from rest_framework import viewsets, permissions
from .models import Device
from .serializers import DeviceSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]



from django.shortcuts import render
from .models import Device

def device_list(request):
    devices = Device.objects.filter(company=request.user.company)
    return render(request, "devices/device_list.html", {"devices": devices})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DeviceRegistrationForm

@login_required
def register_device(request):
    if request.method == "POST":
        form = DeviceRegistrationForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.user = request.user  # Assign device to the current admin
            device.save()
            messages.success(request, "Device registered successfully.")
            return redirect("admin_dashboard")
    else:
        form = DeviceRegistrationForm()

    return render(request, "devices/register_device.html", {"form": form})
