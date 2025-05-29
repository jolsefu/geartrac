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
        elif time_diff <= timedelta(0):
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

import datetime
import os
import subprocess
from django.conf import settings

@shared_task
def backup_database():
    # Configure this based on your database engine
    db = settings.DATABASES['default']
    engine = db['ENGINE']

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    if 'sqlite3' in engine:
        db_path = db['NAME']
        backup_path = os.path.join(backup_dir, f"db_backup_{timestamp}.sqlite3")
        subprocess.run(['cp', db_path, backup_path])
    elif 'postgresql' in engine:
        backup_path = os.path.join(backup_dir, f"db_backup_{timestamp}.sql")
        subprocess.run([
            'pg_dump',
            '-U', db['USER'],
            '-h', db.get('HOST', 'localhost'),
            '-p', str(db.get('PORT', 5432)),
            '-d', db['NAME'],
            '-f', backup_path
        ], check=True, env={**os.environ, 'PGPASSWORD': db['PASSWORD']})
    elif 'mysql' in engine:
        backup_path = os.path.join(backup_dir, f"db_backup_{timestamp}.sql")
        subprocess.run([
            'mysqldump',
            '-u', db['USER'],
            f"-p{db['PASSWORD']}",
            db['NAME']
        ], stdout=open(backup_path, 'w'))
    else:
        raise NotImplementedError(f"Backup not implemented for {engine}")

    return f"Backup created: {backup_path}"
