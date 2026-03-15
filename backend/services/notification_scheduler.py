"""
Notification scheduler for autonomous, agentic email notifications.

This module handles:
1. Scheduled notifications (daily prompts, reminders)
2. Triggered notifications (mood-based follow-ups)
3. Smart scheduling (respecting user preferences and timezones)
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from backend.db.firebase_client import get_db
from backend.db.queries import (
    get_user_profile,
    get_user_mood_history,
    get_user_long_term_memory,
)
from backend.services.email_service import get_email_service

logger = logging.getLogger(__name__)


class NotificationScheduler:
    """Manages notification scheduling and sending"""

    def __init__(self):
        self.email_service = get_email_service()

    def schedule_daily_prompt(self, user_id: str, prompt: str, hour: int = 9) -> bool:
        """
        Schedule a daily journaling prompt notification.

        Args:
            user_id: User to schedule for
            prompt: The journaling prompt
            hour: What hour of day to send (default: 9 AM)

        Returns:
            True if scheduled successfully
        """
        try:
            db = get_db()

            tomorrow = datetime.utcnow() + timedelta(days=1)
            scheduled_time = tomorrow.replace(hour=hour, minute=0, second=0, microsecond=0)

            notification_data = {
                "user_id": user_id,
                "type": "daily_prompt",
                "prompt": prompt,
                "scheduled_time": scheduled_time,
                "sent": False,
                "created_at": datetime.utcnow(),
                "retry_count": 0,
            }

            db.collection("notifications").add(notification_data)
            logger.info(f"✓ Scheduled daily prompt for {user_id} at {scheduled_time}")
            return True

        except Exception as e:
            logger.error(f"Failed to schedule daily prompt: {str(e)}")
            return False

    def schedule_mood_followup(
        self,
        user_id: str,
        mood: str,
        intensity: float,
        message: str
    ) -> bool:
        """
        Schedule a mood-triggered follow-up notification.

        Args:
            user_id: User who logged the mood
            mood: The mood emotion
            intensity: Mood intensity (0-1)
            message: Personalized follow-up message

        Returns:
            True if scheduled successfully
        """
        try:
            db = get_db()

            scheduled_time = datetime.utcnow() + timedelta(hours=24)

            notification_data = {
                "user_id": user_id,
                "type": "mood_followup",
                "mood": mood,
                "intensity": intensity,
                "message": message,
                "scheduled_time": scheduled_time,
                "sent": False,
                "created_at": datetime.utcnow(),
                "retry_count": 0,
            }

            db.collection("notifications").add(notification_data)
            logger.info(f"✓ Scheduled mood followup for {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to schedule mood followup: {str(e)}")
            return False

    def schedule_streak_reminder(self, user_id: str, streak_days: int) -> bool:
        """
        Schedule a streak reminder notification.

        Args:
            user_id: User with active streak
            streak_days: Number of consecutive days

        Returns:
            True if scheduled successfully
        """
        try:
            db = get_db()

            scheduled_time = datetime.utcnow() + timedelta(hours=24)

            notification_data = {
                "user_id": user_id,
                "type": "streak_reminder",
                "streak_days": streak_days,
                "scheduled_time": scheduled_time,
                "sent": False,
                "created_at": datetime.utcnow(),
                "retry_count": 0,
            }

            db.collection("notifications").add(notification_data)
            logger.info(f"✓ Scheduled streak reminder for {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to schedule streak reminder: {str(e)}")
            return False

    async def send_scheduled_notifications(self) -> int:
        """
        Find and send all due notifications.
        Called by background scheduler every N minutes.

        Returns:
            Number of notifications sent
        """
        if not self.email_service:
            logger.warning("Email service not available, skipping notifications")
            return 0

        try:
            db = get_db()
            now = datetime.utcnow()

            due_notifications = (
                db.collection("notifications")
                .where("sent", "==", False)
                .where("scheduled_time", "<=", now)
                .limit(100)
                .stream()
            )

            sent_count = 0

            for doc in due_notifications:
                notification = doc.to_dict()
                notification_id = doc.id

                try:
                    user = get_user_profile(notification["user_id"])
                    if not user:
                        logger.warning(f"User {notification['user_id']} not found")
                        continue

                    success = self._send_notification(user, notification)

                    if success:
                        db.collection("notifications").document(notification_id).update({
                            "sent": True,
                            "sent_at": datetime.utcnow(),
                        })
                        sent_count += 1
                        logger.info(f"✓ Sent notification to {user['email']}")
                    else:
                        retry_count = notification.get("retry_count", 0)
                        if retry_count < 3:
                            db.collection("notifications").document(notification_id).update({
                                "retry_count": retry_count + 1,
                                "last_retry_at": datetime.utcnow(),
                            })
                        else:
                            db.collection("notifications").document(notification_id).update({
                                "failed": True,
                                "failed_at": datetime.utcnow(),
                            })
                            logger.error(f"Notification {notification_id} failed after 3 retries")

                except Exception as e:
                    logger.error(f"Error sending notification {notification_id}: {str(e)}")
                    continue

            logger.info(f"✓ Sent {sent_count} notifications")
            return sent_count

        except Exception as e:
            logger.error(f"Error in send_scheduled_notifications: {str(e)}")
            return 0

    def _send_notification(self, user: Dict[str, Any], notification: Dict[str, Any]) -> bool:
        """
        Route a notification to the correct email_service method based on type.
        All HTML generation is handled by email_service.py — single source of truth.

        Args:
            user: User profile dict (must contain 'email' and 'display_name')
            notification: Notification dict from Firestore

        Returns:
            True if sent successfully
        """
        email = user["email"]
        name = user.get("display_name", "there")
        notification_type = notification.get("type")

        if notification_type == "daily_prompt":
            return self.email_service.send_daily_prompt(
                email=email,
                prompt=notification["prompt"]
            )

        elif notification_type == "mood_followup":
            return self.email_service.send_mood_followup(
                email=email,
                mood=notification["mood"],
                followup_message=notification["message"]
            )

        elif notification_type == "streak_reminder":
            return self.email_service.send_streak_reminder(
                email=email,
                streak_days=notification["streak_days"]
            )

        elif notification_type == "welcome":
            return self.email_service.send_welcome_email(
                email=email,
                name=name
            )

        else:
            logger.warning(f"Unknown notification type: {notification_type}")
            return False


# Global scheduler instance
_scheduler: Optional[NotificationScheduler] = None


def get_notification_scheduler() -> NotificationScheduler:
    """Get or initialize notification scheduler"""
    global _scheduler
    if _scheduler is None:
        _scheduler = NotificationScheduler()
    return _scheduler
