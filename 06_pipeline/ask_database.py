import json
import requests
from pathlib import Path

from generate_sql_ollama import generate_sql
from run_query import execute_select_query
from memory import MemoryManager
from config import PROMPTS_DIR

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"
MEMORY = MemoryManager()  # Initialise le gestionnaire de mémoire

#Charge le prompt d'humanisation
def load_humanize_prompt() -> str:
    path = PROMPTS_DIR / "humanize_prompt.txt"
    return path.read_text(encoding="utf-8")

#Transforme un DataFrame pandas en liste de dictionnaires JSON-like.
def dataframe_to_records(df):
    return df.to_dict(orient="records")

#Humanise les résultats SQL en texte naturel avec Mistral
def humanize_results(question: str, sql: str, results: list, columns: list) -> str:
    base_prompt = load_humanize_prompt()
    
    # Déterminer le contexte pour aide à la désambiguïsation
    context_hints = []
    
    # Vérifier si c'est une requête d'équipes ou d'équipements
    sql_lower = sql.lower()
    if 'dim_equipe' in sql_lower or 'id_equipe' in sql_lower:
        context_hints.append("CONTEXTE: La requête parle d'ÉQUIPES (les gens/équipes de travail)")
    if 'dim_equipement' in sql_lower or 'id_equipement' in sql_lower:
        context_hints.append("CONTEXTE: La requête parle d'ÉQUIPEMENTS (les machines/équipements)")
    
    # Vérifier les colonnes dans les résultats
    if results and isinstance(results[0], dict):
        result_columns = list(results[0].keys())
        if any('equipe' in col.lower() and 'machine' not in col.lower() for col in result_columns):
            context_hints.append("Les résultats contiennent des données sur les ÉQUIPES (id_equipe, nom_equipe...)")
        if 'equipement' in str(result_columns).lower():
            context_hints.append("Les résultats contiennent des données sur les ÉQUIPEMENTS (id_equipement, nom_equipement...)")
    
    results_json = json.dumps(results, ensure_ascii=False, indent=2, default=str)
    context_text = "\n".join(context_hints) if context_hints else ""
    
    prompt = f"""{base_prompt}

{context_text}

Question utilisateur: {question}
Résultats SQL ({len(results)} résultat(s)):
{results_json}

Humanise cette réponse maintenant."""

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
        humanized = data.get("response", "").strip()
        
        # Si la réponse est vide, retourner un fallback
        if not humanized:
            return f"Voici les résultats trouvés: {len(results)} résultat(s) pertinent(s) à votre question."
        
        return humanized
    except Exception as e:
        print(f"❌ Erreur humanisation: {str(e)}")
        return f"Je n'ai pas pu générer une explication détaillée, mais voici les résultats: {len(results)} résultat(s) trouvé(s)."

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

#Fonction principale pour poser une question
def ask(question: str):
    # Récupère le contexte de mémoire (conversation + faits persistants)
    memory_context = MEMORY.get_full_context()
    
    # Génère la réponse avec le contexte de mémoire
    generation = generate_sql(question, memory_context=memory_context)
    
    # Si c'est une réponse textuelle (définition, concept, etc.)
    if generation.get("is_text_response", False):
        answer = generation["sql"]
        MEMORY.add_interaction(question, answer, "text_response")
        
        return {
            "question": question,
            "type": "text_response",
            "answer": answer,
            "valid": True,
            "retrieved_docs": generation.get("retrieved_docs", [])
        }

    # Si la requête n'est pas valide on ne l'exécute pas
    if not generation["valid"]:
        MEMORY.add_interaction(
            question, 
            f"Erreur: {generation['validation_message']}", 
            "sql_query"
        )
        
        return {
            "question": question,
            "type": "sql_query",
            "sql": generation["sql"],
            "valid": False,
            "error": generation["validation_message"],
            "rows": []
        }

    # Exécute la requête sur SQL Server
    try:
        df = execute_select_query(generation["sql"])
    except Exception as e:
        MEMORY.add_interaction(
            question, 
            f"Erreur d'exécution: {str(e)}", 
            "sql_query"
        )
        
        return {
            "question": question,
            "type": "sql_query",
            "sql": generation["sql"],
            "valid": False,
            "error": f"Erreur d'exécution: {str(e)}",
            "rows": []
        }

    # Mémorize la requête réussie
    result_summary = f"{len(df)} lignes retournées"
    MEMORY.add_interaction(question, result_summary, "sql_query")
    
    return {
        "question": question,
        "type": "sql_query",
        "sql": generation["sql"],
        "valid": True,
        "rows_count": len(df),
        "columns": list(df.columns),
        "rows": dataframe_to_records(df)
    }


if __name__ == "__main__":
    print("=== Assistant IA avec Mémoire ===")
    print("Commands spéciaux:")
    print("  /facts - Voir les faits mémorisés")
    print("  /prefs - Voir les préférences")
    print("  /addfact <texte> - Ajouter un fait")
    print("  /addpref <clé> <valeur> - Ajouter une préférence")
    print("  /clear - Effacer la conversation (pas la mémoire persistante)")
    print("  /quit - Quitter\n")
    
    while True:
        user_input = input("Question utilisateur : ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == "/quit":
            print("Bye!")
            break
        
        elif user_input.lower() == "/facts":
            facts = MEMORY.persistent.get_facts()
            if facts:
                print("\n=== Faits Mémorisés ===")
                for f in facts:
                    print(f"- {f}")
            else:
                print("Aucun fait mémorisé")
            print()
            continue
        
        elif user_input.lower() == "/prefs":
            prefs = MEMORY.persistent.get_preferences()
            if prefs:
                print("\n=== Préférences ===")
                for k, v in prefs.items():
                    print(f"- {k}: {v}")
            else:
                print("Aucune préférence définie")
            print()
            continue
        
        elif user_input.lower().startswith("/addfact "):
            fact = user_input[9:].strip()
            MEMORY.persistent.add_fact(fact)
            print(f"✓ Fait ajouté: {fact}\n")
            continue
        
        elif user_input.lower().startswith("/addpref "):
            parts = user_input[9:].split(" ", 1)
            if len(parts) == 2:
                key, value = parts
                MEMORY.persistent.add_preference(key, value)
                print(f"✓ Préférence ajoutée: {key} = {value}\n")
            else:
                print("Usage: /addpref <clé> <valeur>\n")
            continue
        
        elif user_input.lower() == "/clear":
            MEMORY.reset_conversation()
            print("✓ Historique de conversation effacé\n")
            continue
        
        # Question normale
        result = ask(user_input)

        if result["type"] == "text_response":
            print("\n" + result["answer"])
        else:
            if result["valid"]:
                # Générer et afficher la réponse humanisée
                humanized = humanize_results(
                    result["question"], 
                    result["sql"], 
                    result["rows"],
                    result["columns"]
                )
                print("\n" + humanized)
            else:
                # Afficher l'erreur humanisée
                explanation = humanize_error(result["question"], result["error"])
                print("\n" + explanation)
