import json
from pathlib import Path
from config import SCHEMA_DIR, SQL_DIR, RAG_DIR, TESTS_DIR, ARTIFACTS_DIR

def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()

def read_jsonl(path: Path):
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON in {path} at line {line_num}: {exc}") from exc
    return items

def build_corpus():
    docs = []

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

    out_path = ARTIFACTS_DIR / "corpus.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Corpus créé : {out_path}")
    print(f"[OK] Nombre de documents : {len(docs)}")

if __name__ == "__main__":
    build_corpus()