import json
import requests

from generate_sql_ollama import generate_sql
from run_query import execute_select_query

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

#Transforme un DataFrame pandas en liste de dictionnaires JSON-like.
def dataframe_to_records(df):
    return df.to_dict(orient="records")

#Humanise les résultats SQL en texte naturel avec Mistral
def humanize_results(question: str, sql: str, results: list, columns: list) -> str:
    prompt = f"""Tu es un assistant IA qui transforme des résultats de base de données en texte naturel.

Question: {question}
SQL: {sql}
Résultats ({len(results)} lignes): {json.dumps(results, ensure_ascii=False, indent=2, default=str)}
Colonnes: {columns}

Tâche - Écris une réponse INTELLIGENTE et NATURELLE en français:
- Si c'est 1 résultat: affiche le chiffre/données clairement
- Si c'est 2-5 résultats: liste-les avec contexte
- Si c'est 6+ résultats: résume les points clés + tendances (pas besoin de tous les lister)
- Utilise les vraies données de la réponse SQL
- Pas de tableau, pas de code, juste du texte naturel"""

    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
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
        return data.get("response", "").strip()
    except Exception as e:
        return f"Erreur lors de la humanisation: {str(e)}"

#Humanise les erreurs SQL en texte naturel avec Mistral
def humanize_error(question: str, error_message: str) -> str:
    prompt = f"""Tu es un assistant IA.

Question posée: {question}

Erreur rencontrée: {error_message}

Tâche:
Explique cette erreur en langage naturel compréhensible. 
Dis que je ne peux pas répondre à cette question pour l'instant et propose une alternative si possible.
Sois concis. Réponse naturelle uniquement."""

    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
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
        return data.get("response", "").strip()
    except Exception as e:
        return f"Désolé, je n'ai pas pu répondre à votre question: {error_message}"

#Fonction principale pour poser une question, générer le SQL correspondant,
def ask(question: str):
    generation = generate_sql(question)

#Si la requête n’est pas valide on ne l’exécute pas
# sinon on retourne une erreur
    if not generation["valid"]:
        return {
            "question": question,
            "sql": generation["sql"],
            "valid": False,
            "error": generation["validation_message"],
            "rows": []
        }

     #Exécute la requête sur SQL Server
    try:
        df = execute_select_query(generation["sql"])
    except Exception as e:
        return {
            "question": question,
            "sql": generation["sql"],
            "valid": False,
            "error": f"Erreur d'exécution: {str(e)}",
            "rows": []
        }

    return {
        "question": question,
        "sql": generation["sql"],
        "valid": True,
        "rows_count": len(df),
        "columns": list(df.columns),
        "rows": dataframe_to_records(df)
    }


if __name__ == "__main__":
    question = input("Question utilisateur : ").strip()
    result = ask(question)

    print("\n=== SQL généré ===\n")
    print(result["sql"])

    print("\n=== Résultat ===\n")
    if result["valid"]:
        print("Colonnes :", result["columns"])
        print("Nombre de lignes :", result["rows_count"])
        
        print("\n=== Réponse humanisée ===\n")
        humanized = humanize_results(
            question, 
            result["sql"], 
            result["rows"],
            result["columns"]
        )
        print(humanized)
    else:
        print("Erreur :", result["error"])
        print("\n=== Explication humanisée ===\n")
        explanation = humanize_error(question, result["error"])
        print(explanation)