from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from .models import Slip, CustomNotification

@shared_task
def notify_upcoming_returns():
    now = timezone.now()
    slips = Slip.objects.filter(
        currently_active=True,
        for_return=False,
        returned=False,
        declined=False,
    )

    for slip in slips:
        expected = slip.expected_return_date
        if timezone.is_naive(expected):
            expected = timezone.make_aware(expected)

        time_diff = expected - now

        if timedelta(days=1) >= time_diff > timedelta(hours=12):
            message = f"Reminder: Slip #{slip.custom_id} is due for return tomorrow."
        elif timedelta(hours=12) >= time_diff > timedelta(hours=6):
            message = f"Reminder: Slip #{slip.custom_id} is due for return in 12 hours."
        elif timedelta(hours=6) >= time_diff > timedelta(hours=1):
            message = f"Reminder: Slip #{slip.custom_id} is due for return in 6 hours."
        elif timedelta(hours=1) >= time_diff > timedelta(0):
            message = f"Reminder: Slip #{slip.custom_id} is due for return in 1 hour."
        else:
            prev_notification = CustomNotification.objects.filter(
                recipient=slip.slipped_by,
                message=f"Alert: Slip #{slip.custom_id} is overdue for return!"
            ).order_by('-timestamp').first()

            if prev_notification:
                prev_notification.delete()

            message = f"Alert: Slip #{slip.custom_id} is overdue for return!"

        CustomNotification.objects.get_or_create(
            recipient=slip.slipped_by,
            message=message,
        )
