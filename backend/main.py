# backend/main.py
# make sure environment is active: source venv/bin/activate

from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Optional sanity check
assert os.getenv("HF_ENDPOINT"), "HF_ENDPOINT missing"
assert os.getenv("HF_TOKEN"), "HF_TOKEN missing"

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from backend.rag import RAGRetriever
from backend.prompts import build_rag_prompt
from backend.llm import ask_llama

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGRetriever()


class ChatRequest(BaseModel):
    message: str


# ✅ NEW: deduplicate near-identical context blocks
def dedupe_contexts(contexts: list[str]) -> list[str]:
    seen = set()
    unique = []

    for text in contexts:
        key = text[:200].lower()  # semantic fingerprint
        if key not in seen:
            seen.add(key)
            unique.append(text)

    return unique


@app.post("/api/chat")
def chat(req: ChatRequest):
    # 1️⃣ Retrieve chunks
    chunks = rag.retrieve(req.message)
    
    

    raw_contexts = []
    sources = set()

    for c in chunks:
        raw_contexts.append(c["text"])
        sources.add(c["source"])

    # 2️⃣ Deduplicate overlapping definitions
    context_blocks = dedupe_contexts(raw_contexts)

    # 3️⃣ Build prompt (NO sources inside prompt)
    prompt = build_rag_prompt(
        question=req.message,
        contexts=context_blocks,
    )

    # 4️⃣ Generate answer
    answer = ask_llama(prompt).strip()

    # 5️⃣ Append source ONCE (application responsibility)
    if sources:
        answer += "\n\nSOURCE: " + ", ".join(sorted(sources))

    return {"reply": answer}
