from backend.ai.mood_analysis import analyse_mood
from backend.ai.response_generator import generate_reflective_response
from backend.ai.profile_updater import update_user_profile_memory


def main():
    today_entry = (
        "I feel really overwhelmed with school right now. "
        "I have multiple deadlines this week and I keep falling behind."
    )

    recent_entries = [
        {
            "timestamp": "2026-03-11",
            "text": "I have been feeling stressed about assignments.",
            "mood_label": "stress",
            "intensity": 0.7,
        },
        {
            "timestamp": "2026-03-12",
            "text": "I am anxious about an upcoming exam.",
            "mood_label": "anxiety",
            "intensity": 0.8,
        },
        {
            "timestamp": "2026-03-13",
            "text": "I did not sleep well and felt behind all day.",
            "mood_label": "overwhelm",
            "intensity": 0.75,
        },
    ]

    user_profile_memory = """
Common stressors:
- coursework deadlines
- exam pressure

Recurring emotions:
- stress
- anxiety

Helpful strategies:
- short walks
- making a small task list

Support preferences:
- calm
- reflective
"""

    try:
        print("Starting mood analysis...")
        mood = analyse_mood(today_entry)
        print("Mood analysis done.")
        print(mood.model_dump())
        print()

        print("Starting response generation...")
        response = generate_reflective_response(
            today_entry=today_entry,
            recent_entries=recent_entries,
            user_profile_memory=user_profile_memory,
        )
        print("Response generation done.")
        print(response.model_dump())
        print()

        print("Starting profile update...")
        updated_memory = update_user_profile_memory(
            recent_entries=recent_entries + [
                {
                    "timestamp": "2026-03-14",
                    "text": today_entry,
                    "mood_label": mood.emotion,
                    "intensity": mood.intensity,
                }
            ],
            current_memory=user_profile_memory,
        )
        print("Profile update done.")
        print(updated_memory.model_dump())
        print()

    except Exception as e:
        print("Test flow failed:")
        print(type(e).__name__)
        print(e)


if __name__ == "__main__":
    main()