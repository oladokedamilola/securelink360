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
