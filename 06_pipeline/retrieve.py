import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL_NAME, FAISS_INDEX_PATH, DOCS_PATH, TOP_K

class Retriever:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.index = faiss.read_index(str(FAISS_INDEX_PATH))
        self.documents = json.loads(DOCS_PATH.read_text(encoding="utf-8"))

    def search(self, query: str, top_k: int = TOP_K):
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype("float32")

        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:
                results.append({
                    "score": float(score),
                    "document": self.documents[idx]
                })
        return results

if __name__ == "__main__":
    retriever = Retriever()
    query = input("Question: ")
    results = retriever.search(query)

    for i, r in enumerate(results, start=1):
        print("\n" + "=" * 80)
        print(f"Resultat {i} | score={r['score']:.4f}")
        print(f"Source: {r['document']['source']}")
        print(r["document"]["text"][:1000])