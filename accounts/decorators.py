from django.core.exceptions import PermissionDenied
from functools import wraps
from django.utils import timezone

def check_company_and_license(user):
    """
    Helper function to validate company assignment & license.
    """
    if not user.company:
        raise PermissionDenied("You are not assigned to a company.")

    license = getattr(user.company, "license", None)
    if not license:
        raise PermissionDenied("No active license found for your company.")

    if license.expiry_date < timezone.now().date():
        raise PermissionDenied("Your company's license has expired.")

    if license.active_seats >= license.max_seats:
        raise PermissionDenied("Your company's license seat limit has been reached.")


def role_required(*allowed_roles):
    """
    Restrict access to specific user roles + valid company license.
    Usage:
        @role_required("admin", "manager")
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("You must be logged in.")

            # Company & license validation
            check_company_and_license(request.user)

            if request.user.role not in allowed_roles:
                raise PermissionDenied("You do not have permission to access this page.")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# --- Shortcuts ---
def company_admin_required(view_func):
    return role_required("admin")(view_func)

def manager_required(view_func):
    return role_required("manager")(view_func)

def viewer_required(view_func):
    return role_required("viewer")(view_func)

def employee_required(view_func):
    return role_required("employee")(view_func)
