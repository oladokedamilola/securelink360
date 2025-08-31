# middleware/company_scope.py
from django.http import HttpResponseForbidden

class CompanyAccessMiddleware:
    """Ensures that logged-in users can only access their company's data."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.user.company:
                return HttpResponseForbidden("You are not assigned to a company.")
        return self.get_response(request)

from django.http import HttpResponseForbidden
from django.utils.timezone import now

class CompanyAccessMiddleware:
    """
    Ensures that logged-in users can only access their company's data.
    Also enforces license validity (expiry + seat limits).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # User must be assigned to a company
            if not request.user.company:
                return HttpResponseForbidden("You are not assigned to a company.")

            # Ensure company has a license
            license = getattr(request.user.company, "license", None)
            if not license:
                return HttpResponseForbidden("Your company does not have an active license.")

            # Check license expiry
            if license.expiry_date < now().date():
                return HttpResponseForbidden("Your company license has expired.")

            # Enforce seat limits (optional, but good practice)
            active_users = request.user.company.users.filter(is_active=True).count()
            if active_users > license.seats:
                return HttpResponseForbidden("Your company has exceeded the number of allowed users.")

        return self.get_response(request)
