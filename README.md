# CS Tutor Bot – RAG-based Course Assistant (COMP-2140)

A full-stack **Retrieval-Augmented Generation (RAG)** chatbot designed to help students understand course material for **COMP-2140 (Compilers)** without revealing full solutions.

The system uses **course assignment PDFs as ground truth**, retrieves relevant sections using embeddings + FAISS, and generates **grounded, non-hallucinating explanations** using a LLaMA-based language model.

---

## ✨ Features

- 📄 Ingests and indexes all COMP-2140 assignment PDFs (A1–A5)
- 🔎 Semantic search using **MiniLM embeddings + FAISS**
- 🧠 Grounded answers using **LLaMA (via Hugging Face Inference Endpoint)**
- 🚫 Prevents hallucinations and solution leakage
- 🧩 Full-stack architecture:
  - **Backend:** FastAPI (Python)
  - **Frontend:** React + TypeScript
- 📎 Source-aware responses (assignment-specific grounding)

---

## 🏗️ System Architecture

```bash
PDF Assignments (A1–A5)
↓
Text Chunking
↓
Sentence Embeddings (MiniLM)
↓
FAISS Vector Index
↓
Relevant Context Retrieval
↓
Grounded Prompt Construction
↓
LLaMA Chat Completion
↓
Student-Facing Response (React UI)

---
```
## 📂 Project Structure
```bash
cs-tutor-bot/
├── backend/
│ ├── main.py # FastAPI app & API routes
│ ├── rag.py # PDF loading, chunking, FAISS retrieval
│ ├── llm.py # Hugging Face LLaMA API client
│ ├── prompts.py # Strict RAG prompt construction
│ └── test_rag_*.py # RAG verification scripts
│
├── frontend/
│ ├── src/
│ │ ├── App.tsx # React UI
│ │ └── index.tsx
│ └── index.css
│
├── data/
│ └── compilers/
│ ├── 2140_A1.pdf
│ ├── 2140_A2.pdf
│ ├── 2140_A3.pdf
│ ├── 2140_A4.pdf
│ └── 2140_A5.pdf
│
├── requirements.txt
└── README.md


---
```
## 🚀 Setup Instructions

### 1️⃣ Backend Setup

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

export HF_ENDPOINT=https://<your-endpoint>.aws.endpoints.huggingface.cloud
export HF_TOKEN=hf_XXXXXXXXXXXXXXXX

Start the backend:

uvicorn backend.main:app --reload


Backend runs at:
👉 http://127.0.0.1:8000


2️⃣ Frontend Setup
cd frontend
npm install
npm start


Frontend runs at:
👉 http://localhost:3000


```
## Screenshots:

![Frontend UI](screenshots/ui.png)
![Frontend UI2](screenshots/ui-2.png)