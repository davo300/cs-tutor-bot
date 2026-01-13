# backend/llm.py

import os
import requests
from typing import Tuple


def get_hf_config() -> Tuple[str, str]:
    """
    Lazily fetch Hugging Face endpoint and token.
    Safe for uvicorn reloads and multiprocessing.
    """
    endpoint = os.getenv("HF_ENDPOINT")
    token = os.getenv("HF_TOKEN")

    if not endpoint or not token:
        raise RuntimeError(
            "HF_ENDPOINT or HF_TOKEN not set. "
            "Ensure .env is loaded before importing llm."
        )

    return endpoint, token


def ask_llama(prompt: str) -> str:
    endpoint, token = get_hf_config()

    url = endpoint.rstrip("/") + "/generate"

    payload = {
        "inputs": prompt,
        "parameters": {
            # Hard cap to prevent semantic looping
            "max_new_tokens": 90,

            # Low temperature = stable definitions
            "temperature": 0.1,

            # Stop BEFORE repetition or metadata
            "stop": [
                "\n\nSOURCE:",
                "\nSOURCE:",
                "\nREFERENCE MATERIAL",
                "\nQUESTION:",
            ],
        },
    }

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=120,
    )

    response.raise_for_status()
    data = response.json()

    return data["generated_text"].strip()
