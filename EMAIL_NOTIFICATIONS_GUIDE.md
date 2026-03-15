# Email Notifications Implementation Guide

## Overview

Email notifications are a key agentic feature of GenAI Genesis. The system autonomously sends:
- **Daily prompts** - Morning journaling prompts
- **Mood-triggered follow-ups** - Intelligent responses to emotional patterns
- **Streak reminders** - Motivation to maintain consistency
- **Welcome emails** - Onboarding for new users

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (User Action)                   │
│  User saves journal entry / checks in mood / completes task │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 Backend API Endpoint                        │
│  diary.py: POST /journal-entry                              │
│  moods.py: POST /mood-entry                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              AI Analysis & Decision Making                  │
│  - Run agent loop (analyze mood/emotions)                   │
│  - Determine if follow-up needed (risk level, themes)       │
│  - Generate personalized message                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          NotificationScheduler (Agentic Decision)           │
│  _schedule_notifications()                                  │
│  - Decides notification type based on mood                  │
│  - Schedules for optimal time (next day)                    │
│  - Stores in Firestore notifications collection             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│        Background Scheduler (Every 5 minutes)               │
│  TaskScheduler → APScheduler                                │
│  - Queries due notifications                                │
│  - Sends via email provider                                 │
│  - Marks as sent in Firestore                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            Email Service (Provider Abstraction)             │
│  SendGrid / SMTP → User's Email                             │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Email Service (`backend/services/email_service.py`)

**Purpose:** Abstract email sending across providers

**Classes:**
- `EmailProvider` - Abstract base for email providers
- `SendGridProvider` - SendGrid REST API implementation
- `SMTPProvider` - Gmail/SMTP implementation
- `EmailService` - Main service (singleton pattern)

**Key Methods:**
```python
send_notification(recipient_email, subject, html_content) → bool
send_welcome_email(email, name) → bool
send_daily_prompt(email, prompt) → bool
send_mood_followup(email, mood, message) → bool
send_streak_reminder(email, streak_days) → bool
```

**Provider Selection (via ENV):**
```bash
EMAIL_PROVIDER=sendgrid        # Default
SENDGRID_API_KEY=...

# OR

EMAIL_PROVIDER=smtp
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=app-password
```

### 2. Notification Scheduler (`backend/services/notification_scheduler.py`)

**Purpose:** Autonomously schedule notifications based on user behavior

**Key Methods:**
```python
schedule_daily_prompt(user_id, prompt, hour=9) → bool
schedule_mood_followup(user_id, mood, intensity, message) → bool
schedule_streak_reminder(user_id, streak_days) → bool
send_scheduled_notifications() → int  # Called every 5 mins
```

**Agentic Decision Logic:**
```python
# In diary.py _schedule_notifications()
if mood_result.needs_followup or mood_result.risk_level in ["medium", "high"]:
    # Autonomously schedule follow-up
    scheduler.schedule_mood_followup(...)
```

### 3. Background Task Scheduler (`backend/services/scheduler.py`)

**Purpose:** Run notification sender job on schedule

**Technology:** APScheduler (background job scheduler)

**Jobs:**
- `send_notifications_job()` - Every 5 minutes
  - Finds due notifications in Firestore
  - Sends via email provider
  - Marks as sent/failed
  - Retries up to 3 times

**Lifecycle:**
```python
@app.on_event("startup")
def startup_event():
    start_background_tasks()  # Starts scheduler

@app.on_event("shutdown")
def shutdown_event():
    stop_background_tasks()   # Stops scheduler
```

### 4. Integration Points (`backend/api/diary.py`)

**When journal entry saved:**
```python
@router.post("/journal-entry")
async def save_journal_entry(data, user_id):
    # ... run agent loop ...
    
    # AGENTIC: Autonomously decide if notification needed
    await _schedule_notifications(user_id, agent_result.mood, data.entry)
```

**Notification scheduling logic:**
```python
async def _schedule_notifications(user_id, mood_result, entry_text):
    if mood_result.needs_followup or mood_result.risk_level in ["medium", "high"]:
        message = _generate_followup_message(mood_result, entry_text)
        scheduler.schedule_mood_followup(user_id, mood_result.emotion, ...)
```

## Firestore Schema

### Notifications Collection

```firestore
notifications/{doc_id}
{
  "user_id": "firebase_uid",
  "type": "mood_followup|daily_prompt|streak_reminder|welcome",
  "subject": "Email subject line",
  "html_content": "<html>...</html>",
  "scheduled_time": Timestamp,
  "sent": false,
  "created_at": Timestamp,
  
  // For mood_followup
  "mood": "sad|happy|anxious|...",
  "intensity": 0.75,
  "message": "Personalized text",
  
  // For daily_prompt
  "prompt": "What's on your mind?",
  
  // For retry tracking
  "retry_count": 0,
  "last_retry_at": Timestamp,
  "sent_at": Timestamp,
  "failed": false,
  "failed_at": Timestamp
}
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Key packages:
- `APScheduler>=3.10.4` - Background job scheduling
- `sendgrid>=6.10.0` - Email sending (optional if using SMTP)

### 2. Configure Email Provider

**Option A: SendGrid (Recommended)**

```bash
# In .env
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxx
EMAIL_FROM=noreply@genai-genesis.com
```

Get API key:
1. Go to [SendGrid Console](https://app.sendgrid.com)
2. Settings → API Keys
3. Create new API key with "Mail Send" permission

**Option B: Gmail SMTP**

```bash
# In .env
EMAIL_PROVIDER=smtp
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

Get app password:
1. Enable 2FA on Gmail account
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Select "Mail" and "Windows Computer"
4. Copy the generated 16-char password

### 3. Update .env

```bash
cp .env.example .env

# Add these variables
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.your-key
EMAIL_FROM=noreply@genai-genesis.com
```

### 4. Firestore Security Rules

```firestore
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Only backend can write notifications
    match /notifications/{notification_id} {
      allow read: if request.auth.uid == resource.data.user_id;
      allow write: if false;  // Backend only via service account
    }
  }
}
```

## Testing

### Test 1: Send Email via EmailService

```python
from backend.services.email_service import get_email_service

service = get_email_service()
success = service.send_welcome_email(
    email="test@example.com",
    name="Test User"
)
print(f"Email sent: {success}")
```

### Test 2: Schedule Notification

```python
from backend.services.notification_scheduler import get_notification_scheduler

scheduler = get_notification_scheduler()
success = scheduler.schedule_mood_followup(
    user_id="user123",
    mood="sad",
    intensity=0.8,
    message="We noticed you're feeling down. That's okay."
)
print(f"Scheduled: {success}")

# Check Firestore notifications collection
# Should see a new document with type: "mood_followup"
```

### Test 3: Full Backend Test

```bash
# Start backend
python -m uvicorn backend.api.main:app --reload

# In another terminal, test journal entry
curl -X POST http://localhost:8000/api/journal-entry \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "How are you feeling?",
    "entry": "<p>I am feeling sad today</p>"
  }'

# Check:
# 1. Console log: "✓ Scheduled mood follow-up for user123"
# 2. Firestore: New notification in notifications collection
# 3. Background job runs every 5 mins: Sends email
```

### Test 4: Manual Notification Send

```python
import asyncio
from backend.services.notification_scheduler import get_notification_scheduler

async def test():
    scheduler = get_notification_scheduler()
    sent = await scheduler.send_scheduled_notifications()
    print(f"Sent {sent} notifications")

asyncio.run(test())
```

## Email Templates

### Welcome Email
```
Subject: Welcome to GenAI Genesis! 🌱

Shows:
- Feature highlights
- Getting started guide
- Call to action button
```

### Daily Prompt Email
```
Subject: ✍️ Your Daily Journaling Prompt

Shows:
- The daily prompt in highlighted box
- Instructions
- Button to journal
```

### Mood Follow-up Email
```
Subject: 💭 We noticed you're feeling [mood]

Shows:
- Empathetic acknowledgment
- Personalized message (AI-generated from mood analysis)
- Suggestions for coping
- Link to dashboard
```

### Streak Reminder Email
```
Subject: 🔥 Keep your [N]-day streak going!

Shows:
- Celebration of consistency
- Motivation message
- Button to continue journaling
```

## Agentic Behavior

### Decision Points

1. **Mood-Triggered Notifications:**
   ```python
   if mood_result.needs_followup or mood_result.risk_level in ["medium", "high"]:
       # Autonomously schedule follow-up
   ```

2. **Personalized Messages:**
   ```python
   def _generate_followup_message(mood_result, entry_text):
       # Generate contextual message based on emotion/intensity
       # Could be enhanced with OpenAI for AI-generated messages
   ```

3. **Optimal Timing:**
   ```python
   scheduled_time = datetime.utcnow() + timedelta(hours=24)
   # Send next day (respects user timezone if implemented)
   ```

### Future Enhancements

- [ ] **AI-Generated Messages** - Use OpenAI to personalize each message
- [ ] **User Preferences** - Store notification preferences (frequency, time, types)
- [ ] **Timezone-Aware Scheduling** - Send at preferred time in user's timezone
- [ ] **Smart Timing** - Send when user is most likely to read (engagement score)
- [ ] **A/B Testing** - Test different message templates for engagement
- [ ] **Unsubscribe** - Allow users to opt-out of notification types

## Monitoring

### Check Notification Status

```python
from backend.db.firebase_client import get_db

db = get_db()

# Recent sent notifications
sent = db.collection("notifications") \
    .where("sent", "==", True) \
    .order_by("sent_at", direction="DESCENDING") \
    .limit(10) \
    .stream()

for doc in sent:
    notif = doc.to_dict()
    print(f"{notif['user_id']}: {notif['type']} - {notif['sent_at']}")

# Failed notifications (retry > 3)
failed = db.collection("notifications") \
    .where("failed", "==", True) \
    .stream()

for doc in failed:
    notif = doc.to_dict()
    print(f"Failed: {notif['user_id']} - {notif['type']}")
```

### Logs

Background scheduler logs appear in console:
```
✓ Notification job: sent 3 notifications
```

Email service logs:
```
✓ Email sent to user@example.com
✓ Scheduled mood follow-up for user123
```

## Troubleshooting

### "Email service not available"
- Check EMAIL_PROVIDER is set in .env
- Check API key/SMTP credentials are valid
- Run: `python -m backend.services.email_service`

### "Background scheduler not running"
- Check backend started with: `python -m uvicorn backend.api.main:app --reload`
- Check logs for "✓ Background tasks started"
- APScheduler needs event loop

### "Notifications not sending"
- Check notifications in Firestore (should have scheduled_time <= now)
- Check email address is valid
- Check email provider credentials
- Manually trigger: `await scheduler.send_scheduled_notifications()`

### "Notification in Firestore but not sent"
- Check `sent` field is still False
- Check `scheduled_time` is in the past
- Check `retry_count` < 3
- Check backend scheduler is running
- Wait 5 minutes for job to run

## Performance

- **Scheduler Job:** 5-minute interval
- **Batch Size:** 100 notifications per run
- **Timeout:** N/A (async)
- **Failed Notification Retention:** 3 retries, then marked failed

## Security

✅ **Implemented:**
- Only backend (service account) can write notifications
- User can only read their own notifications
- Email addresses from user profile (not user input)
- HTML content sanitized by email providers

⚠️ **To Implement:**
- Email unsubscribe links
- Notification preference management
- Rate limiting (no more than 3 per day per user)

---

**Status:** ✅ Email notifications fully implemented and integrated
