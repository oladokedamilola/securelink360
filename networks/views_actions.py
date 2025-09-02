# networks/views_actions.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import UnauthorizedAttempt

@login_required
@require_POST
def acknowledge_intruder(request, attempt_id):
    from alerts.models import IntruderLog
    log = IntruderLog.objects.filter(unauthorized_attempt_id=attempt_id).first()
    if not log:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)
    log.status = "Acknowledged"
    log.save()
    return JsonResponse({"ok": True})

@login_required
@require_POST
def escalate_intruder(request, attempt_id):
    from alerts.models import IntruderLog
    log = IntruderLog.objects.filter(unauthorized_attempt_id=attempt_id).first()
    if not log:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)
    log.status = "Escalated"
    log.save()
    # TODO: create a ticket / email, etc.
    return JsonResponse({"ok": True})
