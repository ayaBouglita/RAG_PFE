import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL_NAME, FAISS_INDEX_PATH, DOCS_PATH, ARTIFACTS_DIR

CORPUS_PATH = ARTIFACTS_DIR / "corpus.json"

def load_corpus():
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))

def build_index():
    docs = load_corpus()
    texts = [doc["text"] for doc in docs]

    print("[INFO] Chargement du modèle d'embedding...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    print("[INFO] Génération des embeddings...")
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    ).astype("float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    faiss.write_index(index, str(FAISS_INDEX_PATH))
    DOCS_PATH.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Index FAISS sauvegardé : {FAISS_INDEX_PATH}")
    print(f"[OK] Documents sauvegardés : {DOCS_PATH}")
    print(f"[OK] Taille de l'index : {index.ntotal}")

if __name__ == "__main__":
    build_index()