from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
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
            if not request.user.is_authenticated:
                messages.warning(request, "You must be logged in to access this page.")
                return redirect("login")

            if request.user.role not in allowed_roles:
                messages.error(request, "You do not have permission to access this page.")
                return redirect("home")  # change "home" to whatever your safe default is

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
