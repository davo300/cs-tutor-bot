# backend/main.py

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


@app.post("/api/chat")
def chat(req: ChatRequest):
    contexts = rag.retrieve(req.message)

    prompt = build_rag_prompt(
        question=req.message,
        contexts=contexts
    )

    reply = ask_llama(prompt)

    return {"reply": reply}
