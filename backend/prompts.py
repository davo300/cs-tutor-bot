# backend/prompts.py

def build_rag_prompt(question: str, contexts: list[dict]) -> str:
    context_blocks = []

    for c in contexts:
        context_blocks.append(
            f"SOURCE: {c['source']}\n{c['text']}"
        )

    context_text = "\n\n---\n\n".join(context_blocks)

    return f"""
You are a university-level COMP-2140 tutor.

RULES:
- Use ONLY the provided sources
- When multiple files are mentioned across sources, list ALL of them
- Cite the assignment number (A1–A5) when relevant"

COURSE MATERIAL:
{context_text}

QUESTION:
{question}

ANSWER (no code, no full solutions):
"""
