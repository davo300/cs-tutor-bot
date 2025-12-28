# backend/llm.py
import os
import requests

HF_ENDPOINT = os.getenv("HF_ENDPOINT")
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_ENDPOINT or not HF_TOKEN:
    raise RuntimeError("HF_ENDPOINT or HF_TOKEN not set")

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}


def ask_llama(messages, max_tokens=300, temperature=0.7):
    """
    messages: list of {role: 'system'|'user'|'assistant', content: str}
    """
    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    response = requests.post(
        f"{HF_ENDPOINT}/v1/chat/completions",
        headers=HEADERS,
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]
