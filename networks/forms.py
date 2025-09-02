from django import forms
from .models import Network

class NetworkForm(forms.ModelForm):
    class Meta:
        model = Network
        fields = ["name", "description", "visibility"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "visibility": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "name": "Network Name",
            "description": "Description",
            "visibility": "Visibility",
        }   