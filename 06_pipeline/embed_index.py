import json
import faiss #bibliothèque de recherche de similarité vectorielle
import numpy as np #bibliothèque pour manipuler les tableaux de données
from sentence_transformers import SentenceTransformer #bibliothèque pour générer des embeddings à partir de textes
from config import EMBEDDING_MODEL_NAME, FAISS_INDEX_PATH, DOCS_PATH, ARTIFACTS_DIR

#Chemin du corpus
CORPUS_PATH = ARTIFACTS_DIR / "corpus.json"

#Chargement du corpus
def load_corpus():
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))

#Construction de l'index 
def build_index():
    docs = load_corpus()
    texts = [doc["text"] for doc in docs]

#chargement du modèle d'embedding
    print("[INFO] Chargement du modèle d'embedding...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

#Génération des embeddings
    print("[INFO] Génération des embeddings...")

    embeddings = model.encode(  
        texts, #Liste de textes à encoder
        convert_to_numpy=True,  #Convertit les embeddings en tableau numpy
        normalize_embeddings=True, #Normalise les embeddings pour que la similarité soit basée sur le produit scalaire
        show_progress_bar=True  #Affiche une barre de progression pendant l'encodage
    ).astype("float32") #FAISS nécessite que les données soient en float32

    dimension = embeddings.shape[1] #taille du vecteur d'embedding
    index = faiss.IndexFlatIP(dimension) #Index de similarité basé sur le produit scalaire (Inner Product)
    index.add(embeddings) #Ajoute les embeddings à l'index

    faiss.write_index(index, str(FAISS_INDEX_PATH)) #sauvegarde l’index dans faiss_index.bin 
    DOCS_PATH.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8") #sauvegarde les documents dans documents.json

    print(f"[OK] Index FAISS sauvegardé : {FAISS_INDEX_PATH}")
    print(f"[OK] Documents sauvegardés : {DOCS_PATH}")
    print(f"[OK] Taille de l'index : {index.ntotal}")

if __name__ == "__main__":
    build_index()