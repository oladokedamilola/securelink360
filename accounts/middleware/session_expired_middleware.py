# middleware/session_expired_middleware.py
from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings

class SessionExpiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Session is valid, continue
            return self.get_response(request)

        # Only check paths that require login
        if request.path != settings.LOGIN_URL and request.session.session_key:
            messages.warning(request, "Your session has expired. Please log in again.")
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)
