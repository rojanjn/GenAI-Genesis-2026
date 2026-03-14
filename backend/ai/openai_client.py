import os
from openai import OpenAI

MODEL_NAME = "openai/gpt-oss-120b"
DEFAULT_MAX_TOKENS = 1000

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "test"),
    base_url="https://vjioo4r1vyvcozuj.us-east-2.aws.endpoints.huggingface.cloud/v1",
    timeout=60.0,
)


def chat_completion(messages, max_tokens=DEFAULT_MAX_TOKENS, temperature=0.3):
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    choice = resp.choices[0]
    message = choice.message

    if message.content is None:
        print("Model returned no message content.")
        print("Finish reason:", choice.finish_reason)
        print("Reasoning:", getattr(message, "reasoning", None))
        print("Full response:")
        print(resp)
        raise ValueError(
            "Model response content was None. Increase max_tokens or simplify the prompt."
        )

    return message.content