# devices/views.py
from rest_framework import viewsets, permissions
from .models import Device
from .serializers import DeviceSerializer
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DeviceRegistrationForm
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Device, DeviceLog
from .forms import DeviceRegistrationForm


User = get_user_model()

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]


@login_required
def my_devices(request):
    devices = Device.objects.filter(user=request.user)
    return render(request, "companies/devices/my_devices.html", {"devices": devices})

@login_required
def update_device(request, pk):
    device = get_object_or_404(Device, pk=pk, user=request.user)
    if request.method == "POST":
        form = DeviceRegistrationForm(request.POST, instance=device)
        if form.is_valid():
            updated_device = form.save()
            # Log update
            DeviceLog.objects.create(
                user=request.user,
                device=updated_device,
                action="update",
                details=f"Updated fields for device {updated_device.name}"
            )
            messages.success(request, "Device updated successfully.")
            return redirect("my_devices")
    else:
        form = DeviceRegistrationForm(instance=device)
    return render(request, "companies/devices/update_device.html", {"form": form})

@login_required
def delete_device(request, pk):
    device = get_object_or_404(Device, pk=pk, user=request.user)
    if request.method == "POST":
        # Log delete before removing
        DeviceLog.objects.create(
            user=request.user,
            device=device,
            action="delete",
            details=f"Deleted device {device.name}"
        )
        device.delete()
        messages.success(request, "Device deleted successfully.")
        return redirect("my_devices")
    return render(request, "companies/devices/delete_device.html", {"device": device})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DeviceRegistrationForm

@login_required
def register_device(request):
    # Optional: restrict to company admins only
    if not request.user.is_company_admin:
        messages.error(request, "You do not have permission to register devices.")
        return redirect("admin_dashboard")
    user = request.user
    if request.method == "POST":
        form = DeviceRegistrationForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.user = request.user  # Assign device to the current admin
            device.save()  # Triggers the device_state_changed signal
            messages.success(request, f"Device '{device.name}' registered successfully.")
            if user.role == User.Roles.ADMIN:
                return redirect("admin_dashboard")
            elif user.role == User.Roles.MANAGER:
                return redirect("manager_dashboard")
            return redirect("employee_dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DeviceRegistrationForm()

    return render(request, "companies/devices/register_device.html", {"form": form})

