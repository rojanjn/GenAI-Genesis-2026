"""
Services module - Contains business logic services like email, notifications, etc.
"""

from backend.services.email_service import get_email_service, EmailService
from backend.services.notification_scheduler import get_notification_scheduler, NotificationScheduler
from backend.services.scheduler import get_task_scheduler, start_background_tasks, stop_background_tasks

__all__ = [
    "get_email_service",
    "EmailService",
    "get_notification_scheduler",
    "NotificationScheduler",
    "get_task_scheduler",
    "start_background_tasks",
    "stop_background_tasks",
]
