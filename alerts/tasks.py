from celery import shared_task
from django.utils import timezone
from .models import UserAlertPreference
from .services import NotificationService


@shared_task
def process_reminders():
    """
    Celery task to process reminders every 2 hours
    This is scheduled in settings.py CELERY_BEAT_SCHEDULE
    """
    print("=== Running reminder processing task ===")
    
    notification_service = NotificationService()
    results = notification_service.process_reminders()
    
    print(f"Processed {len(results)} alerts")
    for result in results:
        print(f"Alert: {result['alert_title']} - Sent: {result.get('sent', 0)}, Snoozed: {result.get('snoozed', 0)}")
    
    return {
        'success': True,
        'processed': len(results),
        'results': results
    }


@shared_task
def reset_expired_snoozes():
    """
    Celery task to reset expired snoozes at midnight
    This is scheduled in settings.py CELERY_BEAT_SCHEDULE
    """
    print("=== Running snooze reset task ===")
    
    now = timezone.now()
    
    # Find all preferences where snooze has expired
    expired_snoozes = UserAlertPreference.objects.filter(
        is_snoozed=True,
        snooze_until__lt=now
    )
    
    count = expired_snoozes.count()
    
    # Reset them
    expired_snoozes.update(
        is_snoozed=False,
        snooze_until=None
    )
    
    print(f"Reset {count} expired snoozes")
    
    return {
        'success': True,
        'reset_count': count
    }


@shared_task
def send_alert_task(alert_id, is_reminder=False):
    """
    Celery task to send alert asynchronously
    Can be called manually or scheduled
    """
    notification_service = NotificationService()
    result = notification_service.send_alert(alert_id, is_reminder)
    return result