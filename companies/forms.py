from django import forms
from .models import Company

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "domain"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Company Name"}),
            "domain": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. acme.com"}),
        }
        labels = {
            "name": "Company Name",
            "domain": "Company Domain",
        }
        help_texts = {
            "domain": "Enter the domain associated with your company (e.g., acme.com).",
        }
        error_messages = {
            "name": {
                "max_length": "The company name is too long.",
            },
            "domain": {
                "invalid": "Enter a valid domain name.",
            },
        }
        
    def clean_domain(self):
        domain = self.cleaned_data.get("domain")
        if Company.objects.filter(domain=domain).exists():
            raise forms.ValidationError("A company with this domain already exists.")
        return domain
    

from django import forms
from .models import SecuritySetting

class SecuritySettingForm(forms.ModelForm):
    class Meta:
        model = SecuritySetting
        fields = ["mfa_required", "password_min_length", "session_timeout_minutes"]
        widgets = {
            "mfa_required": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "password_min_length": forms.NumberInput(attrs={"class": "form-control"}),
            "session_timeout_minutes": forms.NumberInput(attrs={"class": "form-control"}),
        }
        labels = {
            "mfa_required": "Require Multi-Factor Authentication",
            "password_min_length": "Minimum Password Length",
            "session_timeout_minutes": "Session Timeout (minutes)",
        }   
        help_texts = {
            "mfa_required": "Enable or disable multi-factor authentication for all users.",
            "password_min_length": "Set the minimum length for user passwords.",
            "session_timeout_minutes": "Set the duration of inactivity before a user is logged out.",
        }
        