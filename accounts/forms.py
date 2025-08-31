# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from .models import User, UserInvite
from django.contrib.auth import get_user_model

User = get_user_model()
class AdminRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ["company_name", "email", "password1", "password2"]


class InviteUserForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=UserInvite.ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter user email"})
    )

    class Meta:
        model = UserInvite
        fields = ["email", "role"]



class InviteAcceptanceForm(SetPasswordForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(user, *args, **kwargs)


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "role", "is_active"]


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)