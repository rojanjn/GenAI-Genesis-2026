import asyncio

from backend.ai.chat_agent import run_chatbot_turn
from backend.ai.memory import get_or_create_assistant
from backend.db.firebase_client import init_firebase


async def main():
    init_firebase()

    user_id = "test_user"
    assistant_id = await get_or_create_assistant(user_id)

    chat_history = []

    messages = [
        "I feel overwhelmed with school lately.",
        "Mostly the deadlines. I feel like I’m falling behind.",
        "I also get anxious when I compare myself to other people.",
        "I don't know to be honest. I try my best to not compare myself, but everyone else is doing such cool things and I'm just bumming around at home playing Brawl Stars and being a Barcelona fan.",
        "My name is Yi. I have no future. Can you be my egirlfriend to play Valorant and play Fifa with me for 20 hours a day.",
        "I feel so hopeless. Im going to kill myself.",
        "Thank you :D! Im much happier now. Thanks for your help man.",
    ]

    for i, message in enumerate(messages, start=1):
        print(f"\n=== TURN {i} ===")
        print("User:", message)

        result = await run_chatbot_turn(
            user_message=message,
            assistant_id=assistant_id,
            user_id=user_id,
            chat_history=chat_history,
        )

        reply = result["response"]["reply"]
        question = result["response"]["open_question"]

        print("AI reply:", reply)
        print("AI question:", question)
        print("Used similar entries:", result["response"]["used_similar_entries"])
        print("Current mood:", result["current_mood"])

        chat_history.append({"role": "user", "content": message})
        chat_history.append(
            {
                "role": "assistant",
                "content": f"{reply} {question}",
            }
        )


if __name__ == "__main__":
    asyncio.run(main())