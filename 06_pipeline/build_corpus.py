import json
from pathlib import Path
from config import SCHEMA_DIR, SQL_DIR, ARTIFACTS_DIR

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("[WARN] pdfplumber non installé - les PDFs ne seront pas traités")

def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()

def read_jsonl(path: Path):
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items

def read_pdf(path: Path) -> str:
    """Extrait tout le texte d'un PDF (définitions, notions, explications)"""
    if not PDF_SUPPORT:
        return ""
    
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num} ---\n{page_text}"
        return text.strip()
    except Exception as e:
        print(f"[ERREUR] Impossible de lire {path}: {e}")
        return ""

def build_corpus():
    docs = []
    
    # Schéma de la base de données (référence)
    schema_path = SCHEMA_DIR / "schema_description.md"
    if schema_path.exists():
        docs.append({
            "source": "schema_description.md",
            "type": "markdown",
            "text": read_text_file(schema_path)
        })
        print(f"[OK] Schéma chargé: schema_description.md")

    # PDFs - DÉSACTIVÉS (l'assistant répond directement aux questions générales)
    # Les PDFs ne sont plus traités car l'assistant est maintenant un assistant généraliste

    # Exemples SQL - SOURCE ESSENTIELLE pour Retriever
    sql_path = SQL_DIR / "sql_examples.jsonl"
    if sql_path.exists():
        for item in read_jsonl(sql_path):
            docs.append({
                "source": "sql_examples.jsonl",
                "type": "sql_example",
                "text": json.dumps(item, ensure_ascii=False)
            })
        print(f"[OK] Exemples SQL chargés")

    # Sauvegarde du corpus au format JSON
    out_path = ARTIFACTS_DIR / "corpus.json"
    out_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Corpus créé : {out_path}")
    print(f"[OK] Nombre total de documents : {len(docs)}")

if __name__ == "__main__":
    build_corpus()
