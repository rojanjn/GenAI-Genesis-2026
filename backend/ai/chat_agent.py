from .memory import load_user_profile
from .chat_response_generator import generate_chat_response
from .agent import _profile_to_text
from .mood_analysis import analyse_mood

from backend.embeddings.embedding_service import generate_embedding
from backend.embeddings.similarity_search import find_similar_entries
from backend.db.queries import get_all_entries


def _filter_entries_by_mood(entries: list[dict], target_mood: str) -> list[dict]:
    if not target_mood:
        return entries

    filtered = []
    for entry in entries:
        entry_mood = entry.get("mood_label")
        if entry_mood == target_mood:
            filtered.append(entry)

    return filtered


async def run_chatbot_turn(
    user_message: str,
    assistant_id: str,
    user_id: str,
    chat_history: list[dict],
) -> dict:
    profile = await load_user_profile(assistant_id)
    profile_memory_text = _profile_to_text(profile)

    mood_result = analyse_mood(user_message)
    current_mood = mood_result.emotion

    message_embedding = generate_embedding(user_message)
    past_entries = get_all_entries(user_id)

    mood_matched_entries = _filter_entries_by_mood(past_entries, current_mood)
    candidate_entries = mood_matched_entries if len(mood_matched_entries) >= 3 else past_entries

    similar_results = find_similar_entries(
        new_embedding=message_embedding,
        entries=candidate_entries,
        top_k=3,
    )

    print("---- Retrieval debug ----")
    print("Current mood:", current_mood)
    print("Past entries loaded:", len(past_entries))
    print("Mood matched entries:", len(mood_matched_entries))
    print("Candidate entries:", len(candidate_entries))

    for score, entry in similar_results:
        print(f"score={score:.4f} | text={entry.get('text', 'No text found')}")
    print("-------------------------")

    similar_entries = [
        {
            "text": entry.get("text"),
            "timestamp": entry.get("timestamp"),
            "entry_id": entry.get("entry_id"),
        }
        for score, entry in similar_results
    ]

    print("Similar entries retrieved:")
    for entry in similar_entries:
        print(entry.get("text", ""))

    response = generate_chat_response(
        user_message=user_message,
        chat_history=chat_history,
        similar_entries=similar_entries,
        user_profile_memory=profile_memory_text,
    )

    return {
        "response": response,
        "similar_entries": similar_entries,
        "current_mood": current_mood,
    }