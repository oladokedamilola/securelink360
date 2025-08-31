from django.contrib.auth.models import User
from companies.models import Announcement


def notify_announcement(announcement):
    from companies.models import Notification

    if announcement.scope == "company":
        recipients = User.objects.filter(company=announcement.company)
    else:
        recipients = User.objects.filter(manager=announcement.manager)

    for user in recipients:
        Notification.objects.create(
            user=user,
            message=f"New {announcement.get_scope_display()} announcement: {announcement.message[:50]}"
        )
