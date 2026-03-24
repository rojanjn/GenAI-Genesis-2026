import json

from .openai_client import chat_completion
from .prompts import MOOD_ANALYSIS_SYSTEM_PROMPT
from .schemas import MoodAnalysisResult


def analyse_mood(entry_text: str) -> MoodAnalysisResult:
    user_prompt = f"""
    Journal entry:
    {entry_text}

    Analyse this entry and return only valid JSON.

    Requirements:
    - choose exactly 1 primary emotion
    - intensity must be a number between 0.0 and 1.0
    - themes must contain 1 to 3 short items
    - risk_level must be one of: none, low, medium, high
    - needs_followup must be true or false
    - reasoning_summary must be short and factual
    - do not treat casual slang, humour, or exaggeration by itself as high risk
    - only assign high risk if the entry clearly suggests acute danger or inability to stay safe

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
        try:
            raw_response = chat_completion(messages, max_tokens=600, temperature=0.1)
        except Exception as e:
            error_msg = str(e)

            if "endpoint is paused" in error_msg or "400" in error_msg:
                raise RuntimeError(
                    "API endpoint is down or paused.\n"
                    "👉 Update or restart your Hugging Face endpoint URL in mood_analysis.py.\n"
                    "Current endpoint is not active."
                )

            raise e

        print("Raw mood response:")
        print(raw_response)

        try:
            parsed = json.loads(raw_response)
            return MoodAnalysisResult(**parsed)
        except json.JSONDecodeError:
            print("Retrying mood analysis due to JSON error...")

    raise ValueError("Model repeatedly returned invalid JSON for mood analysis.")