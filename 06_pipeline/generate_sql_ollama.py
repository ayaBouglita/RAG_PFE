import json
import re
import requests

from retrieve import Retriever
from validate_sql import validate_sql
from config import PROMPTS_DIR

#URL et modèle pour OLLAMA
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

#Fonction pour charger le prompt système depuis un fichier
def load_system_prompt() -> str:
    path = PROMPTS_DIR / "system_prompt.txt"
    return path.read_text(encoding="utf-8")

#prend les documents retrouvés dans retrieve.py et
#extrait leur texte et les concatène avec des séparateurs
def build_context(results):
    chunks = []
    for r in results:
        chunks.append(r["document"]["text"])
    return "\n\n---\n\n".join(chunks)

#Fonction pour extraire uniquement la partie SQL de la réponse du modèle
def extract_sql_only(text: str) -> str:
    text = text.strip()

#Si le modèle a répondu avec : SELECT...on garde seulement ce bloc.
    text = text.replace("```sql", "```")
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.upper().startswith("SELECT") or part.upper().startswith("WITH"):
                text = part
                break

#Analyse ligne par ligne
    lines = text.splitlines()
    kept = []

#Garde seulement les lignes SQL et ignore les lignes vides
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        #Si la ligne commence par un mot-clé SQL, on la garde
        if stripped.upper().startswith(("SELECT", "WITH", "FROM", "JOIN", "LEFT JOIN", "RIGHT JOIN",
                                        "INNER JOIN", "FULL JOIN", "WHERE", "GROUP BY", "ORDER BY",
                                        "HAVING", "UNION", "AND", "OR")):
            kept.append(line)
            continue
        #Dès que le modèle commence à expliquer, on coupe.
        if kept:
            upper = stripped.upper()
            if upper.startswith(("POUR ", "CETTE ", "EXPLICATION", "NOTE", "IL S", "LE RÉSULTAT", "RESULTAT")):
                break
             
            #Si la ligne ressemble à une phrase naturelle et pas à du SQL, on coupe
            if re.match(r"^[A-Za-zÀ-ÿ].*", stripped) and not re.search(r"\b(AS|TOP|SUM|AVG|MIN|MAX|COUNT|LAG|OVER|NULLIF)\b", upper):
                break

            kept.append(line)
        else:
            continue
    #recompose le SQL , Force le ";" final
    sql = "\n".join(kept).strip()

    sql = sql.rstrip(";").strip() + ";"
    return sql

#Fonction principale pour générer la requête SQL 
# à partir de la question utilisateur
def generate_sql(question: str, memory_context: str = ""):
    retriever = Retriever()
    results = retriever.search(question, top_k=5) #On récupère les 5 documents les plus proches.

    #On construit le prompt pour OLLAMA en combinant le prompt système,
    #  le contexte des documents récupérés et la question utilisateur.
    system_prompt = load_system_prompt()
    context = build_context(results)

    # Construction du prompt utilisateur avec la mémoire
    memory_section = f"{memory_context}\n" if memory_context else ""
    
    user_prompt = f"""{memory_section}Contexte (exemples SQL, données disponibles):
{context}

Question utilisateur:
{question}""".strip()
    #Appel à Ollama
    payload = {
        "model": OLLAMA_MODEL,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False
    }
    #Envoi de la requête à OLLAMA et récupération de la réponse
    response = requests.post(
        OLLAMA_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=120
    )
    response.raise_for_status() #Vérification HTTP

    #raw_content = texte brut du modèle
    #content = SQL nettoyé (ou réponse textuelle si définition)
    data = response.json() 
    raw_content = data.get("response", "").strip() 
    
    # Détecte si c'est une réponse textuelle (définition) ou SQL
    is_sql_response = (
        raw_content.upper().strip().startswith("SELECT") or 
        raw_content.upper().strip().startswith("WITH") or
        "SELECT" in raw_content.upper() or
        "FROM" in raw_content.upper()
    )
    
    if is_sql_response:
        content = extract_sql_only(raw_content)
        is_valid, message = validate_sql(content)
    else:
        # C'est une réponse textuelle (définition)
        content = raw_content
        is_valid = True
        message = "Réponse textuelle (pas de SQL nécessaire)"

    return {
        "question": question,
        "sql": content,
        "raw_response": raw_content,
        "valid": is_valid,
        "validation_message": message,
        "retrieved_docs": results,
        "is_text_response": not is_sql_response
    }

#Exemple d'utilisation
if __name__ == "__main__":
    question = input("Question utilisateur : ").strip()
    result = generate_sql(question)

    print("\n=== Réponse brute du modèle ===\n")
    print(result["raw_response"])

    print("\n=== SQL extrait ===\n")
    print(result["sql"])

    print("\nValidation :", result["valid"], "-", result["validation_message"])