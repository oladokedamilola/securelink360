# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import User
from companies.models import Company
from .forms import AdminRegistrationForm


def register(request):
    if request.method == "POST":
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            company_name = form.cleaned_data["company_name"]
            email = form.cleaned_data["email"]

            # Create company
            company = Company.objects.create(name=company_name)

            # Create admin user
            user = User.objects.create_user(
                email=email,
                password=form.cleaned_data["password1"],
                role=User.Roles.ADMIN,
                company=company
            )

            login(request, user)
            messages.success(request, f"Welcome to SecureLink360, {company_name}!")
            return redirect("admin_dashboard")

    else:
        form = AdminRegistrationForm()
    return render(request, "auth/register.html", {"form": form})


# accounts/views.py
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = "auth/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.is_company_admin():
            return "/dashboard/admin/"
        elif user.is_manager():
            return "/dashboard/manager/"
        elif user.is_viewer():
            return "/dashboard/viewer/"
        return "/dashboard/employee/"



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .models import UserInvite, User
from .forms import InviteUserForm
from .decorators import company_admin_required
import uuid
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import InviteUserForm, EditUserForm
from .models import UserInvite, Company

User = settings.AUTH_USER_MODEL


@login_required
@company_admin_required
def user_management(request):
    company = request.user.company
    users = company.users.all()
    invites = company.invites.filter(accepted=False)
    return render(request, "user_management.html", {
        "users": users,
        "invites": invites,
    })

@login_required
@company_admin_required
def send_invite(request):
    if request.method == "POST":
        form = InviteUserForm(request.POST)
        if form.is_valid():
            invite = form.save(commit=False)
            invite.company = request.user.company
            invite.invited_by = request.user
            invite.save()

            # Send email with tokenized link
            invite_link = request.build_absolute_uri(f"/invite/accept/{invite.token}/")
            send_mail(
                "You're invited to SecureLink 360",
                f"Hello,\n\nYou have been invited to join {request.user.company.name} on SecureLink 360.\n\nClick the link to accept: {invite_link}\n\nThis link expires in 7 days.",
                settings.DEFAULT_FROM_EMAIL,
                [invite.email],
            )
            messages.success(request, f"Invitation sent to {invite.email}")
            return redirect("admin_users")
    else:
        form = InviteUserForm()

    return render(request, "companies/admin/send_invite.html", {"form": form})

@login_required
@company_admin_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id, company=request.user.company)
    if request.method == "POST":
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user_management")
    else:
        form = EditUserForm(instance=user)
    return render(request, "edit_user.html", {"form": form, "user": user})


@login_required
@company_admin_required
def deactivate_user(request, user_id):
    user = get_object_or_404(User, id=user_id, company=request.user.company)
    user.is_active = False
    user.save()
    return redirect("user_management")


@login_required
@company_admin_required
def resend_invite(request, invite_id):
    invite = get_object_or_404(UserInvite, id=invite_id, company=request.user.company)

    if invite.is_expired():
        invite.token = uuid.uuid4()
        invite.created_at = timezone.now()
        invite.save()

    invite_url = request.build_absolute_uri(reverse("accept_invite", args=[invite.token]))
    send_mail(
        subject="Your invitation link (resend) - SecureLink360",
        message=f"Here’s your updated invite link: {invite_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invite.email],
    )

    return redirect("user_management")


@login_required
@company_admin_required
def revoke_invite(request, invite_id):
    invite = get_object_or_404(UserInvite, id=invite_id, company=request.user.company)
    invite.delete()
    return redirect("user_management")


from .forms import InviteAcceptanceForm
from django.contrib.auth import get_user_model, login

User = get_user_model()

def accept_invite(request, token):
    invite = get_object_or_404(UserInvite, token=token, accepted=False)

    if invite.is_expired():
        return render(request, "companies/invite_expired.html")

    if request.method == "POST":
        user = User(email=invite.email, company=invite.company)
        form = InviteAcceptanceForm(request.POST, user=user)
        if form.is_valid():
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.role = invite.role  # ✅ use the admin-assigned role
            user.set_password(form.cleaned_data["new_password1"])
            user.save()

            invite.accepted = True
            invite.save()

            login(request, user)
            return redirect("user_dashboard")
    else:
        form = InviteAcceptanceForm(user=User(email=invite.email))

    return render(request, "companies/accept_invite.html", {"invite": invite, "form": form})
