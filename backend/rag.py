# backend/rag.py

import os
from typing import List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

# -----------------------------
# Configuration
# -----------------------------

DATA_DIR = "data/compilers"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

CHUNK_SIZE = 400        # words per chunk
CHUNK_OVERLAP = 50      # overlap for continuity
TOP_K = 3               # chunks to retrieve


# -----------------------------
# PDF loading
# -----------------------------

def load_pdfs(folder_path: str) -> List[str]:
    documents = []

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(".pdf"):
            continue

        path = os.path.join(folder_path, filename)
        reader = PdfReader(path)

        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if text.strip():
            documents.append(text)

    return documents


# -----------------------------
# Chunking
# -----------------------------

def chunk_text(text: str) -> List[str]:
    words = text.split()
    chunks = []

    i = 0
    while i < len(words):
        chunk = words[i : i + CHUNK_SIZE]
        chunks.append(" ".join(chunk))
        i += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


# -----------------------------
# RAG Retriever
# -----------------------------

class RAGRetriever:
    def __init__(self):
        self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.index = None
        self.chunks: List[str] = []

        self._build_index()

    def _build_index(self):
        raw_docs = load_pdfs(DATA_DIR)

        for doc in raw_docs:
            self.chunks.extend(chunk_text(doc))

        if not self.chunks:
            raise RuntimeError("No text chunks were created from PDFs.")

        embeddings = self.embedder.encode(
            self.chunks,
            convert_to_numpy=True,
            show_progress_bar=True
        ).astype("float32")

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

    def retrieve(self, question: str, k: int = TOP_K) -> List[str]:
        query_embedding = self.embedder.encode(
            [question],
            convert_to_numpy=True
        ).astype("float32")

        distances, indices = self.index.search(query_embedding, k)
        return [self.chunks[i] for i in indices[0]]


# -----------------------------
# Local test
# -----------------------------

if __name__ == "__main__":
    rag = RAGRetriever()

    results = rag.retrieve("What is a recursive descent parser?")

    for i, r in enumerate(results, 1):
        print(f"\n--- Chunk {i} ---\n{r[:500]}...")
