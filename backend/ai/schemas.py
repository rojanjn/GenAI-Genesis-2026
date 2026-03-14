from typing import List
from pydantic import BaseModel, Field


class MoodAnalysisResult(BaseModel):
    emotion: str
    intensity: float = Field(ge=0.0, le=1.0)
    themes: List[str]
    risk_level: str
    needs_followup: bool
    reasoning_summary: str


class GeneratedResponse(BaseModel):
    reflection: str
    open_question: str
    coping_suggestion: str


class UserProfileMemory(BaseModel):
    common_stressors: List[str]
    recurring_emotions: List[str]
    helpful_strategies: List[str]
    support_preferences: List[str]
    recent_patterns: List[str]
    summary: str