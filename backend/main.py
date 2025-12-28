from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.llm import ask_llama
from backend.rag import RAGRetriever


rag = RAGRetriever()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
def chat(req: ChatRequest):
    retrieved_chunks = rag.retrieve(req.message)

    context_text = "\n\n".join(retrieved_chunks)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a university computer science tutor.\n"
                "Use ONLY the provided course material to explain concepts.\n"
                "Do NOT give full solutions or code.\n"
                "Guide the student step-by-step.\n\n"
                f"Course material:\n{context_text}"
            ),
        },
        {
            "role": "user",
            "content": req.message,
        },
    ]

    reply = ask_llama(messages)
    return {"reply": reply}

