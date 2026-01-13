# backend/prompts.py
from typing import List


def build_rag_prompt(
    question: str,
    contexts: List[str],
) -> str:
    """
    Build a prompt where the model produces ONLY the answer text.
    Sources are appended by the backend, not the model.
    """

    context_text = "\n\n".join(contexts)

    return f"""
You are a university-level COMP-2140 tutor.

Rules:
- Answer ONLY the given question.
- Give a direct definition only.
- Do NOT include examples unless explicitly asked.
- Do NOT explain related concepts.
- Limit the answer to at most 2 sentences.

REFERENCE MATERIAL:
-------------------
{context_text}
-------------------

QUESTION:
{question}

ANSWER:
""".strip()
