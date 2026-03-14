import json
from typing import List, Dict, Optional

from .openai_client import chat_completion
from .prompts import PROFILE_UPDATE_SYSTEM_PROMPT
from .schemas import UserProfileMemory


def update_user_profile_memory(
    recent_entries: List[Dict],
    current_memory: Optional[str] = None,
) -> UserProfileMemory:
    entries_text = "\n".join(
        (
            f"- {entry.get('timestamp', 'unknown time')} | "
            f"mood={entry.get('mood_label', 'unknown')} | "
            f"intensity={entry.get('intensity', 'unknown')}\n"
            f"{entry.get('text', '')}"
        )
        for entry in recent_entries
    ) if recent_entries else "No recent entries."

    memory_text = current_memory or "No existing memory."

    user_prompt = f"""
CURRENT MEMORY:
{memory_text}

RECENT ENTRIES:
{entries_text}

Return only valid JSON.
Do not include markdown.
Do not include backticks.
Do not include reasoning.
Keep every list short.
Keep the summary to one sentence under 30 words.

Use exactly this structure:
{{
  "common_stressors": [],
  "recurring_emotions": [],
  "helpful_strategies": [],
  "support_preferences": [],
  "recent_patterns": [],
  "summary": ""
}}
"""

    messages = [
        {"role": "system", "content": PROFILE_UPDATE_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    for _ in range(2):
        raw_response = chat_completion(messages, max_tokens=1200, temperature=0.2)

        print("Raw profile update response:")
        print(raw_response)

        try:
            parsed = json.loads(raw_response)
            return UserProfileMemory(**parsed)
        except json.JSONDecodeError:
            print("Retrying profile update due to JSON error...")

    raise ValueError("Model repeatedly returned invalid JSON for profile update.")