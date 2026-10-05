# backend/rag.py

import os
from typing import List, Dict
import faiss
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from pathlib import Path
from backend.text_processing import clean_text, chunk_text, extract_page_text

DATA_DIR = str(Path(__file__).resolve().parent.parent / "data" / "compilers")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

CHUNK_SIZE = 250
CHUNK_OVERLAP = 40
TOP_K = 3      # necessary to grab relevent info


def load_pdfs(folder_path: str) -> List[Dict]:
    docs = []
    for filename in sorted(os.listdir(folder_path)):
        if not filename.lower().endswith(".pdf"):
            continue
        reader = PdfReader(os.path.join(folder_path, filename))
        for number, page in enumerate(reader.pages, start=1):
            text = extract_page_text(page)
            if text:
                docs.append({"source": filename, "page": number, "text": text})
    return docs


class RAGRetriever:
    def __init__(self):
        self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.index = None
        self.chunks: List[Dict] = []
        self._build_index()

    def _build_index(self):
        docs = load_pdfs(DATA_DIR)

        for doc in docs:
            self.chunks.extend(chunk_text(doc["text"], doc["source"], doc["page"]))

        texts = [c["text"] for c in self.chunks]

        if not texts:
            raise ValueError(f"No extractable PDF text found in {DATA_DIR}")

        embeddings = self.embedder.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True
        ).astype("float32")

        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

        print(f"[RAG] Indexed {len(self.chunks)} chunks")

    def retrieve(self, question: str, k: int = TOP_K) -> List[Dict]:
        if k <= 0:
            return []
        q = self.embedder.encode([question], convert_to_numpy=True).astype("float32")
        _, idxs = self.index.search(q, min(k, len(self.chunks)))
        return [self.chunks[i] for i in idxs[0]]
