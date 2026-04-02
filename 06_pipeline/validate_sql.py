import re

FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "MERGE", "EXEC", "EXECUTE"
]

FORBIDDEN_SQL_PATTERNS = [
    "LIMIT",
    "ILIKE",
    "SERIAL"
]

def validate_sql(sql: str) -> tuple[bool, str]:
    sql_upper = sql.upper().strip()

    if not sql_upper.startswith("SELECT") and not sql_upper.startswith("WITH"):
        return False, "La requête doit commencer par SELECT ou WITH."

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql_upper):
            return False, f"Mot-clé interdit détecté : {keyword}"

    for pattern in FORBIDDEN_SQL_PATTERNS:
        if re.search(rf"\b{pattern}\b", sql_upper):
            return False, f"Syntaxe non compatible SQL Server détectée : {pattern}"

    if re.search(r"\b(POUR|EXPLICATION|RÉSULTAT|RESULTAT|QUESTION UTILISATEUR)\b", sql_upper):
        return False, "Texte explicatif détecté dans la sortie."

    return True, "SQL valide"