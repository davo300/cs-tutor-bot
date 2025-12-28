def tutor_prompt(context: list[str], question: str) -> str:
    joined_context = "\n\n".join(context)

    return f"""
You are a university computer science tutor.

Use the provided course material to explain concepts.
DO NOT give full solutions or final answers.
Guide the student with intuition and steps.

Course material:
{joined_context}

Student question:
{question}

Answer:
"""
