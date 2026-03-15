import os
import pytest
from dotenv import load_dotenv
import ssl
import certifi
import asyncio
from datetime import datetime

ssl._create_default_https_context = ssl.create_default_context
os.environ['SSL_CERT_FILE'] = certifi.where()
load_dotenv()
os.environ["SENDGRID_API_KEY"] = os.getenv("SENDGRID_API_KEY")
os.environ["EMAIL_FROM"] = "noreply.airy@gmail.com"

from backend.services.email_service import get_email_service
from backend.services.notification_scheduler import get_notification_scheduler
from backend.db.queries import get_db

TEST_EMAIL = "billy.king.iboss3@gmail.com"
TEST_USER_ID = "YxSCAy7loNVRGkYml2nBXB0duVv2"
TEST_NAME = "Billy King"


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def email_service():
    return get_email_service()


@pytest.fixture
def scheduler():
    return get_notification_scheduler()


# ============================================================================
# Email Service Tests
# ============================================================================

def test_welcome_email(email_service):
    result = email_service.send_welcome_email(email=TEST_EMAIL, name=TEST_NAME)
    assert result == True

def test_daily_prompt(email_service):
    result = email_service.send_daily_prompt(email=TEST_EMAIL, prompt="What made you smile today?")
    assert result == True

def test_mood_followup(email_service):
    result = email_service.send_mood_followup(
        email=TEST_EMAIL,
        mood="anxious",
        followup_message="We noticed you've been feeling anxious. Here are some tips."
    )
    assert result == True

def test_streak_reminder(email_service):
    result = email_service.send_streak_reminder(email=TEST_EMAIL, streak_days=7)
    assert result == True


# ============================================================================
# Notification Routing Tests
# ============================================================================

def test_daily_prompt_routing(scheduler):
    user = {"email": TEST_EMAIL, "display_name": TEST_NAME}
    notification = {"type": "daily_prompt", "prompt": "What made you smile today?"}
    assert scheduler._send_notification(user, notification) == True

def test_mood_followup_routing(scheduler):
    user = {"email": TEST_EMAIL, "display_name": TEST_NAME}
    notification = {
        "type": "mood_followup",
        "mood": "anxious",
        "message": "We noticed you've been feeling anxious."
    }
    assert scheduler._send_notification(user, notification) == True

def test_streak_reminder_routing(scheduler):
    user = {"email": TEST_EMAIL, "display_name": TEST_NAME}
    notification = {"type": "streak_reminder", "streak_days": 7}
    assert scheduler._send_notification(user, notification) == True

def test_unknown_notification_type(scheduler):
    user = {"email": TEST_EMAIL, "display_name": TEST_NAME}
    notification = {"type": "unknown_type"}
    assert scheduler._send_notification(user, notification) == False


# ============================================================================
# Preference Tests
# ============================================================================

def test_preference_update():
    db = get_db()

    db.collection("users").document(TEST_USER_ID).update({
        "preferences.notification_frequency": "daily",
        "preferences.email_reminders": True,
    })

    doc = db.collection("users").document(TEST_USER_ID).get()
    prefs = doc.to_dict().get("preferences", {})
    assert prefs["notification_frequency"] == "daily"
    assert prefs["email_reminders"] == True

def test_preference_disable():
    db = get_db()

    db.collection("users").document(TEST_USER_ID).update({
        "preferences.notification_frequency": "never",
        "preferences.email_reminders": False,
    })

    doc = db.collection("users").document(TEST_USER_ID).get()
    prefs = doc.to_dict().get("preferences", {})
    assert prefs["notification_frequency"] == "never"
    assert prefs["email_reminders"] == False

    # Reset back to daily after test
    db.collection("users").document(TEST_USER_ID).update({
        "preferences.notification_frequency": "daily",
        "preferences.email_reminders": True,
    })


# ============================================================================
# Scheduling + Send Pipeline Test
# ============================================================================

def test_schedule_and_send_now(scheduler):
    db = get_db()

    # Insert a notification in the past so it fires immediately
    db.collection("notifications").add({
        "user_id": TEST_USER_ID,
        "type": "daily_prompt",
        "prompt": "This is a test prompt - does scheduling work?",
        "scheduled_time": datetime(2000, 1, 1),
        "sent": False,
        "retry_count": 0,
        "created_at": datetime.utcnow(),
    })

    # Trigger the sender manually
    sent = asyncio.run(scheduler.send_scheduled_notifications())
    assert sent >= 1
