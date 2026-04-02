import json

from generate_sql_ollama import generate_sql
from run_query import execute_select_query


def dataframe_to_records(df):
    return df.to_dict(orient="records")


def ask(question: str):
    generation = generate_sql(question)

    if not generation["valid"]:
        return {
            "question": question,
            "sql": generation["sql"],
            "valid": False,
            "error": generation["validation_message"],
            "rows": []
        }

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
        print(json.dumps(result["rows"][:20], ensure_ascii=False, indent=2, default=str))
    else:
        print("Erreur :", result["error"])