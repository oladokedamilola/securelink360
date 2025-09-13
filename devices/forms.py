from django import forms
from .models import Device

class DeviceRegistrationForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ["name", "mac_address", "ip_address"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Device Name"}),
            "mac_address": forms.TextInput(attrs={"class": "form-control", "placeholder": "00:1A:2B:3C:4D:5E"}),
            "ip_address": forms.TextInput(attrs={"class": "form-control", "placeholder": "192.168.0.1"}),
        }
        
