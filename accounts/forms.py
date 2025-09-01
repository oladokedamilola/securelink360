# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from .models import User, UserInvite
from django.contrib.auth import get_user_model

User = get_user_model()


class BootstrapFormMixin:
    """
    A mixin to add Bootstrap 5 classes to form fields automatically.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                widget.attrs["class"] = (widget.attrs.get("class", "") + " form-check-input").strip()
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = (widget.attrs.get("class", "") + " form-select").strip()
            else:
                widget.attrs["class"] = (widget.attrs.get("class", "") + " form-control").strip()


class AdminRegistrationForm(BootstrapFormMixin, UserCreationForm):
    company_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter company name"})
    )

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter password"}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm password"}),
    )

    class Meta:
        model = User
        fields = ["company_name", "email", "password1", "password2"]

class EmailAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True, "placeholder": "Enter your email"})
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Enter your password"})
    )

class InviteUserForm(BootstrapFormMixin, forms.ModelForm):
    role = forms.ChoiceField(
        choices=UserInvite.ROLE_CHOICES,
        widget=forms.Select()
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Enter user email"})
    )

    class Meta:
        model = UserInvite
        fields = ["email", "role"]


class InviteAcceptanceForm(BootstrapFormMixin, SetPasswordForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "First name"})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Last name"})
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(user, *args, **kwargs)


class EditUserForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "role", "is_active"]



