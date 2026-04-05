import json
from pathlib import Path
from config import SCHEMA_DIR, SQL_DIR, RAG_DIR, TESTS_DIR, ARTIFACTS_DIR
#lecture d’un fichier texte
def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()

#lecture d’un fichier JSONL
def read_jsonl(path: Path):
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items
#construction du corpus à partir des fichiers markdown et JSONL
def build_corpus():
    docs = []
#lecture des fichiers markdown et ajout au corpus
    md_files = [
        SCHEMA_DIR / "schema_description.md",
        SCHEMA_DIR / "relationships.md",
        SCHEMA_DIR / "sample_data.md",
        RAG_DIR / "business_dictionary.md",
        RAG_DIR / "business_rules.md",
        RAG_DIR / "intents_catalog.md",
    ]

    for path in md_files:
        if path.exists():
            docs.append({
                "source": str(path.name),
                "type": "markdown",
                "text": read_text_file(path)
            })
#lecture des fichiers JSONL et ajout au corpus
    jsonl_files = [
        SQL_DIR / "sql_examples.jsonl",
        RAG_DIR / "rag_documents.jsonl",
        TESTS_DIR / "user_questions_variants.jsonl",
    ]

    for path in jsonl_files:
        if path.exists():
            for item in read_jsonl(path):
                docs.append({
                    "source": str(path.name),
                    "type": "jsonl_record",
                    "text": json.dumps(item, ensure_ascii=False)
                })
#sauvegarde du corpus au format JSON
    out_path = ARTIFACTS_DIR / "corpus.json"
    out_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Corpus créé : {out_path}")
    print(f"[OK] Nombre de documents : {len(docs)}")

if __name__ == "__main__":
    build_corpus()