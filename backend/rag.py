# backend/rag.py

import os
from typing import List, Dict
import faiss
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

DATA_DIR = "data/compilers"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

CHUNK_SIZE = 350
CHUNK_OVERLAP = 50
TOP_K = 8      # necessary to grab relevent info


def load_pdfs(folder_path: str) -> List[Dict]:
    docs = []

    for filename in sorted(os.listdir(folder_path)):
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
            docs.append({
                "source": filename,
                "text": text
            })

    return docs


def chunk_text(text: str, source: str) -> List[Dict]:
    words = text.split()
    chunks = []

    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + CHUNK_SIZE])
        chunks.append({
            "source": source,
            "text": chunk
        })
        i += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


class RAGRetriever:
    def __init__(self):
        self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.index = None
        self.chunks: List[Dict] = []
        self._build_index()

    def _build_index(self):
        docs = load_pdfs(DATA_DIR)

        for doc in docs:
            self.chunks.extend(chunk_text(doc["text"], doc["source"]))

        texts = [c["text"] for c in self.chunks]

        embeddings = self.embedder.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True
        ).astype("float32")

        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

        print(f"[RAG] Indexed {len(self.chunks)} chunks")

    def retrieve(self, question: str, k: int = TOP_K) -> List[Dict]:
        q = self.embedder.encode([question], convert_to_numpy=True).astype("float32")
        _, idxs = self.index.search(q, k)
        return [self.chunks[i] for i in idxs[0]]
