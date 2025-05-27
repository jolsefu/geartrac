from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from .models import Slip, CustomNotification

@shared_task
def notify_upcoming_returns():
    tomorrow = timezone.now() + timedelta(days=1)
    start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)

    slips = Slip.objects.filter(
        expected_return_date__range=(start, end),
        currently_active=True,
        for_return=False,
        returned=False,
        declined=False,
    )

    for slip in slips:
        message = f"Reminder: Slip #{slip.custom_id} is due for return tomorrow."
        CustomNotification.objects.get_or_create(
            recipient=slip.slipped_by,
            message=message,
        )
