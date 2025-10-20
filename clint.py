import os
import requests
from typing import Optional

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class AIClientError(Exception):
    pass


def ask_ai(prompt: str, model: str = "openai/gpt-oss-20b:free", timeout: int = 15) -> str:
    """Send a prompt to the OpenRouter endpoint and return the assistant reply as plain text."""
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    if not OPENROUTER_API_KEY:
        raise AIClientError("OPENROUTER_API_KEY is not set. Please set it in your environment.")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",  # optional but recommended
        "X-Title": "Jarvis AI",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful virtual assistant named Jarvis."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 800,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        raise AIClientError(f"Network error contacting AI provider: {e}")


if __name__ == "__main__":
    try:
        q = input("Ask Jarvis something: ")
        print(ask_ai(q))
    except AIClientError as e:
        print("AI error:", e)