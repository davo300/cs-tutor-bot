from backend.rag import load_pdfs

docs = load_pdfs("data/compilers")

print("Number of PDFs:", len(docs))
for d in docs:
    print(d["source"], "chars:", len(d["text"]))
