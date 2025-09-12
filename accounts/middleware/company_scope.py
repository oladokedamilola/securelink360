# company_network/accounts/middleware/company_scope.py
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.timezone import now

class CompanyAccessMiddleware:
    """
    Ensures that logged-in users can only access their company's data
    and enforces license validity.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            if not request.user.company:
                messages.error(request, "You are not assigned to a company.")
                return redirect("home")

            license = getattr(request.user.company, "license", None)
            if not license:
                messages.error(request, "Your company does not have an active license.")
                return redirect("home")

            if license.expiry_date < now().date():
                messages.error(request, "Your company license has expired.")
                return redirect("home")

            active_users = request.user.company.users.filter(is_active=True).count()
            if active_users > license.seats:
                messages.error(request, "Your company has exceeded the number of allowed users.")
                return redirect("home")

        return self.get_response(request)
