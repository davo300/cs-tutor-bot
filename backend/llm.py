# backend/llm.py

import os
import requests

HF_ENDPOINT = os.getenv("HF_ENDPOINT")  # e.g. https://xxxxx.aws.endpoints.huggingface.cloud
HF_TOKEN = os.getenv("HF_TOKEN")

def ask_llama(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a university-level COMP-2140 tutor. "
                    "You must only answer using the provided course material. "
                    "If the answer is not in the material, say so."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "max_tokens": 400,
        "temperature": 0.0,
    }

    response = requests.post(
        f"{HF_ENDPOINT}/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )

    response.raise_for_status()
    data = response.json()

    return data["choices"][0]["message"]["content"]
