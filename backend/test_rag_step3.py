from backend.rag import RAGRetriever

rag = RAGRetriever()
results = rag.retrieve("What files do we need to submit for A5?")

for r in results:
    print("SOURCE:", r["source"])
    print(r["content"][:250])
    print("-" * 40)
