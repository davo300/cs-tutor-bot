# backend/test_rag_step2.py

from backend.rag import load_pdfs, chunk_text

docs = load_pdfs("data/compilers")

all_chunks = []

for doc in docs:
    chunks = chunk_text(doc["text"], doc["source"])
    all_chunks.extend(chunks)

print("Total chunks:", len(all_chunks))

# Print a few samples
for c in all_chunks[:5]:
    print("\nSOURCE:", c["source"])
    print(c["content"][:200])
