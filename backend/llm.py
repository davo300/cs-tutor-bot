# backend/llm.py

import os
import re
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


def clean_generated_answer(text: str) -> str:
    """Remove exact repeated prose blocks, preserving code and display math."""
    text = text.split("<END_ANSWER>", 1)[0].strip()
    result = []
    seen = set()
    protected = False
    for block in re.split(r"\n[ \t]*\n", text):
        key = re.sub(r"\s+", " ", block).strip()
        contains_markup = "```" in block or "~~~" in block or "$$" in block
        if protected or contains_markup or key not in seen:
            result.append(block)
        if not protected and not contains_markup:
            seen.add(key)
        # Never deduplicate lines inside multi-paragraph code/math blocks.
        for marker in ("```", "~~~", "$$"):
            if block.count(marker) % 2:
                protected = not protected
    return "\n\n".join(result).strip()


def ask_llama(prompt: str) -> str:
    endpoint, token = get_hf_config()

    url = endpoint.rstrip("/") + "/generate"

    payload = {
        "inputs": prompt,
        "parameters": {
            # Leave room for explanations while limiting runaway continuation.
            "max_new_tokens": 256,
            "do_sample": False,
            "repetition_penalty": 1.1,
            "return_full_text": False,

            # Stop BEFORE repetition or metadata
            "stop": [
                "<END_ANSWER>",
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

    return clean_generated_answer(data["generated_text"])
