import os
import pytest
from dotenv import load_dotenv

import ssl
import certifi
ssl._create_default_https_context = ssl.create_default_context
os.environ['SSL_CERT_FILE'] = certifi.where()
load_dotenv()
os.environ["SENDGRID_API_KEY"] = os.getenv("SENDGRID_API_KEY")
os.environ["EMAIL_FROM"] = "noreply.airy@gmail.com"

from backend.services.email_service import get_email_service

@pytest.fixture
def email_service():
    return get_email_service()

def test_welcome_email(email_service):
    result = email_service.send_welcome_email(
        email="billy.king.iboss3@gmail.com",
        name="Test User"
    )
    assert result == True

def test_daily_prompt(email_service):
    result = email_service.send_daily_prompt(
        email="your-test-email@gmail.com",
        prompt="What made you smile today?"
    )
    assert result == True

def test_mood_followup(email_service):
    result = email_service.send_mood_followup(
        email="your-test-email@gmail.com",
        mood="anxious",
        followup_message="We noticed you've been feeling anxious. Here are some tips."
    )
    assert result == True
