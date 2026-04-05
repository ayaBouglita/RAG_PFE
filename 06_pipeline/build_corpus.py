import json
from pathlib import Path
from config import SCHEMA_DIR, SQL_DIR, ARTIFACTS_DIR
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
#construction du corpus minimal - Schéma + exemples SQL seulement
def build_corpus():
    docs = []
#Schéma de la base de données (référence)
    schema_path = SCHEMA_DIR / "schema_description.md"
    if schema_path.exists():
        docs.append({
            "source": "schema_description.md",
            "type": "markdown",
            "text": read_text_file(schema_path)
        })

#Exemples SQL - SOURCE ESSENTIELLE pour Retriever
    sql_path = SQL_DIR / "sql_examples.jsonl"
    if sql_path.exists():
        for item in read_jsonl(sql_path):
            docs.append({
                "source": "sql_examples.jsonl",
                "type": "sql_example",
                "text": json.dumps(item, ensure_ascii=False)
            })
#sauvegarde du corpus au format JSON
    out_path = ARTIFACTS_DIR / "corpus.json"
    out_path.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Corpus créé : {out_path}")
    print(f"[OK] Nombre de documents : {len(docs)}")

if __name__ == "__main__":
    build_corpus()