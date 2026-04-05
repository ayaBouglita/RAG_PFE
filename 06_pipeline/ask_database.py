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
    prompt = f"""Tu es un assistant IA qui transforme des résultats de base de données en texte naturel compréhensible.

Question posée: {question}

Requête SQL exécutée: {sql}

Résultats:
{json.dumps(results, ensure_ascii=False, indent=2, default=str)}

Colonnes: {columns}

Tâche: 
Écris une réponse naturelle et compréhensible en français qui résume les résultats de cette requête. 
Soit concis et clair. Utilise les chiffres et données des résultats.
Réponse naturelle uniquement, pas de format tableau ou code."""

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
    df = execute_select_query(generation["sql"])

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
            result["rows"][:20], 
            result["columns"]
        )
        print(humanized)
    else:
        print("Erreur :", result["error"])