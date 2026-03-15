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
            
            # Calculate tomorrow at specified hour
            tomorrow = datetime.utcnow() + timedelta(days=1)
            scheduled_time = tomorrow.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            notification_data = {
                "user_id": user_id,
                "type": "daily_prompt",
                "prompt": prompt,
                "subject": "✍️ Your Daily Journaling Prompt",
                "html_content": self._generate_prompt_email(prompt),
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
            
            # Schedule for 24 hours from now
            scheduled_time = datetime.utcnow() + timedelta(hours=24)
            
            notification_data = {
                "user_id": user_id,
                "type": "mood_followup",
                "mood": mood,
                "intensity": intensity,
                "subject": f"💭 We noticed you're feeling {mood}",
                "html_content": self._generate_mood_followup_email(mood, message),
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
            
            # Schedule for 24 hours from now
            scheduled_time = datetime.utcnow() + timedelta(hours=24)
            
            notification_data = {
                "user_id": user_id,
                "type": "streak_reminder",
                "streak_days": streak_days,
                "subject": f"🔥 Keep your {streak_days}-day streak going!",
                "html_content": self._generate_streak_email(streak_days),
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
            
            # Find notifications that are due
            due_notifications = db.collection("notifications") \
                .where("sent", "==", False) \
                .where("scheduled_time", "<=", now) \
                .limit(100) \
                .stream()
            
            sent_count = 0
            
            for doc in due_notifications:
                notification = doc.to_dict()
                notification_id = doc.id
                
                try:
                    # Get user profile for email
                    user = get_user_profile(notification["user_id"])
                    if not user:
                        logger.warning(f"User {notification['user_id']} not found")
                        continue
                    
                    # Send email
                    success = self.email_service.send_notification(
                        recipient_email=user["email"],
                        subject=notification.get("subject", "GenAI Genesis Notification"),
                        html_content=notification.get("html_content", "<p>Notification</p>")
                    )
                    
                    # Mark as sent
                    if success:
                        db.collection("notifications").document(notification_id).update({
                            "sent": True,
                            "sent_at": datetime.utcnow(),
                        })
                        sent_count += 1
                        logger.info(f"✓ Sent notification to {user['email']}")
                    else:
                        # Increment retry count
                        retry_count = notification.get("retry_count", 0)
                        if retry_count < 3:
                            db.collection("notifications").document(notification_id).update({
                                "retry_count": retry_count + 1,
                                "last_retry_at": datetime.utcnow(),
                            })
                        else:
                            # Give up after 3 retries
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
    
    def _generate_prompt_email(self, prompt: str) -> str:
        """Generate HTML for daily prompt email"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>📝 Today's Journaling Prompt</h2>
                    
                    <div style="background-color: #f0f4ff; padding: 20px; border-left: 4px solid #6366f1; 
                               margin: 20px 0; border-radius: 4px;">
                        <p style="font-size: 18px; margin: 0;">
                            "{prompt}"
                        </p>
                    </div>
                    
                    <p>Take a few minutes to reflect on this question and write your thoughts.</p>
                    
                    <p>
                        <a href="https://app.genai-genesis.com/journal" 
                           style="display: inline-block; padding: 10px 20px; background-color: #6366f1; 
                                  color: white; text-decoration: none; border-radius: 4px;">
                            Start Journaling
                        </a>
                    </p>
                </div>
            </body>
        </html>
        """
    
    def _generate_mood_followup_email(self, mood: str, message: str) -> str:
        """Generate HTML for mood followup email"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>💭 Personalized Wellness Check-in</h2>
                    
                    <p>We noticed you logged a mood and wanted to follow up.</p>
                    
                    <div style="background-color: #f9f5f0; padding: 20px; border-radius: 4px; margin: 20px 0;">
                        <p>{message}</p>
                    </div>
                    
                    <p>
                        <a href="https://app.genai-genesis.com" 
                           style="display: inline-block; padding: 10px 20px; background-color: #6366f1; 
                                  color: white; text-decoration: none; border-radius: 4px;">
                            View Your Dashboard
                        </a>
                    </p>
                </div>
            </body>
        </html>
        """
    
    def _generate_streak_email(self, streak_days: int) -> str:
        """Generate HTML for streak reminder email"""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>🔥 Amazing Streak!</h2>
                    
                    <p style="font-size: 18px;">
                        You've checked in for <strong>{streak_days} days in a row</strong>! 🎉
                    </p>
                    
                    <p>This consistency is building valuable self-awareness. Keep it up!</p>
                    
                    <p>
                        <a href="https://app.genai-genesis.com/journal" 
                           style="display: inline-block; padding: 10px 20px; background-color: #6366f1; 
                                  color: white; text-decoration: none; border-radius: 4px;">
                            Add Today's Entry
                        </a>
                    </p>
                </div>
            </body>
        </html>
        """


# Global scheduler instance
_scheduler: Optional[NotificationScheduler] = None


def get_notification_scheduler() -> NotificationScheduler:
    """Get or initialize notification scheduler"""
    global _scheduler
    if _scheduler is None:
        _scheduler = NotificationScheduler()
    return _scheduler
