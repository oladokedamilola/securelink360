# networks/context_processors.py
from .models import JoinRequest
from notifications.models import Notification

def network_requests_count(request):
    """
    Context processor to add pending join requests count to all templates
    """
    if request.user.is_authenticated and hasattr(request.user, 'company'):
        if request.user.is_company_admin:
            join_requests_count = JoinRequest.objects.filter(
                network__company=request.user.company, 
                status="pending"
            ).count()
        else:
            join_requests_count = 0
    else:
        join_requests_count = 0
    
    return {
        'join_requests_count': join_requests_count
    }

def unread_notifications_count(request):
    """
    Context processor for unread notifications count
    """
    if request.user.is_authenticated:
        notifications_unread_count = Notification.objects.filter(
            user=request.user, 
            read=False
        ).count()
    else:
        notifications_unread_count = 0
    
    return {
        'notifications_unread_count': notifications_unread_count
    }