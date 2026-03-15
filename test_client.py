from backend.ai.openai_client import chat_completion

messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant. Answer directly in one short sentence. Do not include reasoning.",
    },
    {
        "role": "user",
        "content": "Say hello in one short sentence.",
    },
]

print("Sending request...")

try:
    response = chat_completion(messages, max_tokens=200, temperature=0.1)
    print("Response received:")
    print(response)
except Exception as e:
    print("Request failed:")
    print(type(e).__name__)
    print(e)