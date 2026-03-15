"""
Background task scheduler using APScheduler.
Runs notification sending job on a schedule.
"""

import logging
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from typing import Optional

from backend.services.notification_scheduler import get_notification_scheduler

logger = logging.getLogger(__name__)


class TaskScheduler:
    """Background task scheduler for recurring jobs"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._running = False
    
    def start(self):
        """Start the background scheduler"""
        if self._running:
            logger.warning("Scheduler already running")
            return
        
        try:
            # Add job to send notifications every 5 minutes
            self.scheduler.add_job(
                self._send_notifications_job,
                IntervalTrigger(minutes=5),
                id='send_notifications',
                name='Send scheduled notifications',
                replace_existing=True
            )
            
            # Start scheduler
            self.scheduler.start()
            self._running = True
            logger.info("✓ Background task scheduler started")
            logger.info("  - Notification sender: every 5 minutes")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
    
    def stop(self):
        """Stop the background scheduler"""
        if not self._running:
            return
        
        try:
            self.scheduler.shutdown()
            self._running = False
            logger.info("✓ Background task scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {str(e)}")
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self._running
    
    @staticmethod
    def _send_notifications_job():
        """Job to send scheduled notifications"""
        try:
            notification_scheduler = get_notification_scheduler()
            
            # Run async job in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            sent_count = loop.run_until_complete(
                notification_scheduler.send_scheduled_notifications()
            )
            loop.close()
            
            if sent_count > 0:
                logger.debug(f"Notification job: sent {sent_count} notifications")
            
        except Exception as e:
            logger.error(f"Error in notification job: {str(e)}")


# Global scheduler instance
_scheduler: Optional[TaskScheduler] = None


def get_task_scheduler() -> TaskScheduler:
    """Get or initialize task scheduler"""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler


def start_background_tasks():
    """Start all background tasks (called on app startup)"""
    scheduler = get_task_scheduler()
    scheduler.start()


def stop_background_tasks():
    """Stop all background tasks (called on app shutdown)"""
    scheduler = get_task_scheduler()
    scheduler.stop()
