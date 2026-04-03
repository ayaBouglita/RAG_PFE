import re

#indices = positions des documents trouvés
FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "MERGE", "EXEC", "EXECUTE"
]

#On bloque des syntaxes d’autres SGBD qui ne sont pas compatibles avec SQL Server
FORBIDDEN_SQL_PATTERNS = [
    "LIMIT",
    "ILIKE",
    "SERIAL"
]

#Validation de la requête SQL générée par le LLM
def validate_sql(sql: str) -> tuple[bool, str]:
    sql_upper = sql.upper().strip()

    if not sql_upper.startswith("SELECT") and not sql_upper.startswith("WITH"):
        return False, "La requête doit commencer par SELECT ou WITH."

#Vérification de la présence de mots-clés interdits ou de syntaxes non compatibles
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql_upper):
            return False, f"Mot-clé interdit détecté : {keyword}"

#Vérification de la présence de syntaxes non compatibles avec SQL Server
    for pattern in FORBIDDEN_SQL_PATTERNS:
        if re.search(rf"\b{pattern}\b", sql_upper):
            return False, f"Syntaxe non compatible SQL Server détectée : {pattern}"

#Vérification de la présence de mots-clés indiquant que le LLM 
#a généré du texte explicatif au lieu d'une requête SQL
    if re.search(r"\b(POUR|EXPLICATION|RÉSULTAT|RESULTAT|QUESTION UTILISATEUR)\b", sql_upper):
        return False, "Texte explicatif détecté dans la sortie."

    return True, "SQL valide"