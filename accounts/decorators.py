from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from accounts.models import User

def role_required(*allowed_roles):
    """
    Restrict access to specific user roles.
    Usage:
        @role_required(User.Roles.ADMIN, User.Roles.MANAGER)
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # If not logged in, redirect to custom login page
            if not request.user.is_authenticated:
                messages.warning(request, "You must be logged in to access this page.")
                return redirect(reverse("login"))

            # If role is not allowed, redirect to safe default (dashboard by role)
            if request.user.role not in allowed_roles:
                messages.error(request, "You do not have permission to access this page.")

                # Redirect by role
                if request.user.role == User.Roles.ADMIN:
                    return redirect(reverse("admin_dashboard"))
                elif request.user.role == User.Roles.MANAGER:
                    return redirect(reverse("manager_dashboard"))
                elif request.user.role == User.Roles.EMPLOYEE:
                    return redirect(reverse("employee_dashboard"))
                elif request.user.role == User.Roles.VIEWER:
                    return redirect(reverse("viewer_dashboard"))

                # Fallback
                return redirect(reverse("login"))

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# --- Shortcuts using enums directly ---
def company_admin_required(view_func):
    return role_required(User.Roles.ADMIN)(view_func)

def manager_required(view_func):
    return role_required(User.Roles.MANAGER)(view_func)

def viewer_required(view_func):
    return role_required(User.Roles.VIEWER)(view_func)

def employee_required(view_func):
    return role_required(User.Roles.EMPLOYEE)(view_func)
