import json
from typing import List, Dict, Optional


from .openai_client import chat_completion
from .prompts import RESPONSE_GENERATION_SYSTEM_PROMPT
from .schemas import GeneratedResponse


def generate_reflective_response(
    today_entry: str,
    recent_entries: List[Dict],
    user_profile_memory: Optional[str] = None,
) -> GeneratedResponse:
    recent_text = "\n".join(
        f"- {entry.get('timestamp', 'unknown time')}: {entry.get('text', '')}"
        for entry in recent_entries
    ) if recent_entries else "No recent entries."

    memory_text = user_profile_memory or "No memory yet."

    user_prompt = f"""
USER MEMORY:
{memory_text}

RECENT ENTRIES:
{recent_text}

TODAY ENTRY:
{today_entry}

Return only valid JSON.
Do not include markdown.
Do not include backticks.
Do not include reasoning.
Keep the reflection brief.
Keep the coping suggestion to one small action.

Use exactly this structure:
{{
  "reflection": "It sounds like ...",
  "open_question": "What feels ...?",
  "coping_suggestion": "Try ..."
}}
"""

    messages = [
        {"role": "system", "content": RESPONSE_GENERATION_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    for _ in range(2):
        raw_response = chat_completion(messages, max_tokens=800, temperature=0.3)

        print("Raw response generation output:")
        print(raw_response)

        try:
            parsed = json.loads(raw_response)
            return GeneratedResponse(**parsed)
        except json.JSONDecodeError:
            print("Retrying response generation due to JSON error...")

    raise ValueError("Model repeatedly returned invalid JSON for response generation.")