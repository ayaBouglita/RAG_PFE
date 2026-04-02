import json
import re
import requests

from retrieve import Retriever
from validate_sql import validate_sql
from config import PROMPTS_DIR

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"


def load_system_prompt() -> str:
    path = PROMPTS_DIR / "system_prompt.txt"
    return path.read_text(encoding="utf-8")


def build_context(results):
    chunks = []
    for r in results:
        chunks.append(r["document"]["text"])
    return "\n\n---\n\n".join(chunks)


def extract_sql_only(text: str) -> str:
    text = text.strip()

    text = text.replace("```sql", "```")
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.upper().startswith("SELECT") or part.upper().startswith("WITH"):
                text = part
                break

    lines = text.splitlines()
    kept = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.upper().startswith(("SELECT", "WITH", "FROM", "JOIN", "LEFT JOIN", "RIGHT JOIN",
                                        "INNER JOIN", "FULL JOIN", "WHERE", "GROUP BY", "ORDER BY",
                                        "HAVING", "UNION", "AND", "OR")):
            kept.append(line)
            continue

        if kept:
            upper = stripped.upper()
            if upper.startswith(("POUR ", "CETTE ", "EXPLICATION", "NOTE", "IL S", "LE RÉSULTAT", "RESULTAT")):
                break

            if re.match(r"^[A-Za-zÀ-ÿ].*", stripped) and not re.search(r"\b(AS|TOP|SUM|AVG|MIN|MAX|COUNT|LAG|OVER|NULLIF)\b", upper):
                break

            kept.append(line)
        else:
            continue

    sql = "\n".join(kept).strip()

    sql = sql.rstrip(";").strip() + ";"
    return sql


def generate_sql(question: str):
    retriever = Retriever()
    results = retriever.search(question, top_k=5)

    system_prompt = load_system_prompt()
    context = build_context(results)

    user_prompt = f"""
Contexte récupéré :
{context}

Question utilisateur :
{question}

Tâche :
Génère uniquement une requête SQL Server valide correspondant à la question.

Contraintes obligatoires :
- Utiliser uniquement SQL Server.
- Ne jamais utiliser LIMIT.
- Utiliser TOP pour limiter le nombre de lignes.
- Ne jamais utiliser une syntaxe PostgreSQL, MySQL ou SQLite.
- N'utiliser que les tables et colonnes autorisées.
- Retourner une seule requête SQL.
- Aucun commentaire.
- Aucune explication.
- Aucun texte avant ou après la requête.
- Pas de markdown.
- Pas de ```sql.
- SQL uniquement.
""".strip()

    payload = {
        "model": OLLAMA_MODEL,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=120
    )
    response.raise_for_status()

    data = response.json()
    raw_content = data.get("response", "").strip()
    content = extract_sql_only(raw_content)

    is_valid, message = validate_sql(content)

    return {
        "question": question,
        "sql": content,
        "raw_response": raw_content,
        "valid": is_valid,
        "validation_message": message,
        "retrieved_docs": results
    }


if __name__ == "__main__":
    question = input("Question utilisateur : ").strip()
    result = generate_sql(question)

    print("\n=== Réponse brute du modèle ===\n")
    print(result["raw_response"])

    print("\n=== SQL extrait ===\n")
    print(result["sql"])

    print("\nValidation :", result["valid"], "-", result["validation_message"])