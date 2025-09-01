from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages

class CompanyLicenseMiddleware:
    """
    Ensures:
    - User is tied to a company
    - Company license is active
    - Seat limits are respected
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated and not user.is_superuser:
            company = user.company
            if not company:
                messages.error(request, "You are not assigned to any company.")
                return redirect("logout")

            license = getattr(company, "license", None)
            if not license or not license.is_active():
                messages.error(request, "Your company license has expired.")
                return redirect("logout")

            # Seat validation (extra safety; handled at invite stage normally)
            if company.users.count() > license.seats:
                messages.error(request, "Your company has exceeded its user limit.")
                return redirect("logout")

        return self.get_response(request)
