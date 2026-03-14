import json

from .openai_client import chat_completion
from .prompts import MOOD_ANALYSIS_SYSTEM_PROMPT
from .schemas import MoodAnalysisResult


def analyse_mood(entry_text: str) -> MoodAnalysisResult:
    user_prompt = f"""
Journal entry:
{entry_text}

Return only valid JSON.
Do not include markdown.
Do not include backticks.
Do not include reasoning.
Do not include any text before or after the JSON.

Use exactly this structure:
{{
  "emotion": "stress",
  "intensity": 0.75,
  "themes": ["school", "deadlines"],
  "risk_level": "low",
  "needs_followup": true,
  "reasoning_summary": "Short explanation."
}}
"""

    messages = [
        {"role": "system", "content": MOOD_ANALYSIS_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    for _ in range(2):
        raw_response = chat_completion(messages, max_tokens=600, temperature=0.1)

        print("Raw mood response:")
        print(raw_response)

        try:
            parsed = json.loads(raw_response)
            return MoodAnalysisResult(**parsed)
        except json.JSONDecodeError:
            print("Retrying mood analysis due to JSON error...")

    raise ValueError("Model repeatedly returned invalid JSON for mood analysis.")