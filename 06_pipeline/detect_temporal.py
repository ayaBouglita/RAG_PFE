"""
Détecte si une question implique une évolution temporelle / comparaison / tendance
Retourne le type de graphique approprié et les filtres à appliquer
"""

import re
from enum import Enum

class ChartType(Enum):
    """Types de graphiques disponibles"""
    NONE = "none"
    LINE = "line"  # Évolutions dans le temps
    BAR = "bar"    # Comparaisons
    PIE = "pie"    # Répartitions
    COMBO = "combo"  # Combinaison lignes + barres

class TemporalPattern:
    """Patterns pour détecter les questions temporelles"""
    
    # ÉVOLUTIONS TEMPORELLES (LINE CHART)
    EVOLUTION_PATTERNS = [
        r"évolution\s*(de|du|des|d')",
        r"tendance\s*(de|du|des|d')",
        r"progression\s*(de|du|des|d')",
        r"variation\s*(de|du|des|d')",
        r"augment|baiss|crois|déclin",
        r"par jour|quotidien",
        r"par semaine|hebdomadaire",
        r"par mois|mensuel",
        r"par trimestre|trimestriel",
        r"par an|annuel",
        r"dans le temps",
        r"au fil du temps",
        r"dans le mois|le trimestre|l'année",
        r"mois par mois|jour par jour",
        r"chronologiq",
    ]
    
    # COMPARAISONS (BAR CHART)
    COMPARISON_PATTERNS = [
        r"compar(er|aison)",
        r"différence\s*(entre|avec)",
        r"plus.*que|moins.*que",
        r"vs\.?|versus",
        r"par (équipement|cuve|type|équipe)",
        r"pour chaque",
        r"par rapport à",
        r"contre",
    ]
    
    # RÉPARTITIONS (PIE CHART)
    REPARTITION_PATTERNS = [
        r"répartition\s*(de|du|des|d')",
        r"pourcentage|%",
        r"part\s*(de|du|des|d')",
        r"composition\s*(de|du|des|d')",
        r"ventilation",
        r"par (équipement|cuve|type|source)",
    ]
    
    # MOTS-CLÉS TEMPORELS SPÉCIFIQUES
    TIME_GROUPING_KEYWORDS = {
        "jour|daily|quotidien": "day",
        "semaine|week|hebdomadaire": "week",
        "mois|month|mensuel": "month",
        "trimestre|quarter|trimestriel": "quarter",
        "an|année|year|annuel": "year",
    }

def detect_chart_type(question: str) -> tuple[ChartType, dict]:
    """
    Détecte le type de graphique à générer pour une question.
    
    Returns:
        (ChartType, metadata_dict)
        
    Metadata contains:
        - time_grouping: "day", "week", "month", "quarter", "year"
        - comparison_field: "equipement", "cuve", "type_fuel", etc.
        - chart_title: Titre suggéré
        - measures: List of metrics to display
    """
    
    question_lower = question.lower()
    metadata = {
        "time_grouping": None,
        "comparison_field": None,
        "chart_title": "",
        "measures": [],
        "resource_type": None
    }
    
    # Déterminer le grouping temporel
    for keywords, grouping in TemporalPattern.TIME_GROUPING_KEYWORDS.items():
        pattern = f"({keywords})"
        if re.search(pattern, question_lower):
            metadata["time_grouping"] = grouping
            break
    
    # Si pas de grouping temporel spécifié mais question temporelle → par défaut "month"
    is_temporal_question = any(re.search(p, question_lower) for p in TemporalPattern.EVOLUTION_PATTERNS)
    if is_temporal_question and not metadata["time_grouping"]:
        metadata["time_grouping"] = "month"
    
    # Détecter les champs de comparaison
    if "équipement" in question_lower or "equipment" in question_lower:
        metadata["comparison_field"] = "equipement"
    elif "cuve" in question_lower:
        metadata["comparison_field"] = "cuve"
    elif "type" in question_lower and "fuel" in question_lower:
        metadata["comparison_field"] = "type_fuel"
    elif "équipe" in question_lower or "team" in question_lower:
        metadata["comparison_field"] = "equipe"
    
    # Détecter la ressource (fuel vs électricité)
    if "électricité" in question_lower or "electricity" in question_lower or "kwh" in question_lower:
        metadata["resource_type"] = "electricity"
    elif "fuel" in question_lower:
        metadata["resource_type"] = "fuel"
    
    # Vérifier si c'est une question de répartition
    for pattern in TemporalPattern.REPARTITION_PATTERNS:
        if re.search(pattern, question_lower):
            metadata["chart_title"] = "Répartition des données"
            return ChartType.PIE, metadata
    
    # Vérifier si c'est une comparaison
    if metadata["comparison_field"]:
        for pattern in TemporalPattern.COMPARISON_PATTERNS:
            if re.search(pattern, question_lower):
                metadata["chart_title"] = f"Comparaison par {metadata['comparison_field']}"
                return ChartType.BAR, metadata
    
    # Vérifier si c'est une évolution temporelle
    if metadata["time_grouping"]:
        for pattern in TemporalPattern.EVOLUTION_PATTERNS:
            if re.search(pattern, question_lower):
                grouping_text = {
                    "day": "quotidienne",
                    "week": "hebdomadaire",
                    "month": "mensuelle",
                    "quarter": "trimestrielle",
                    "year": "annuelle"
                }
                resource_text = metadata.get("resource_type", "fuel")
                metadata["chart_title"] = f"Évolution {grouping_text.get(metadata['time_grouping'], '')} - {resource_text}"
                return ChartType.LINE, metadata
    
    # Sinon, pas de graphique
    return ChartType.NONE, metadata


# Exemples de questions avec détection
DETECTION_EXAMPLES = {
    "Quelle est l'évolution de la consommation de fuel par mois en 2025?": (ChartType.LINE, {"time_grouping": "month"}),
    "Quelle est la consommation d'électricité pour chaque équipement?": (ChartType.BAR, {"comparison_field": "equipement"}),
    "Quel est la répartition de la consommation par cuve?": (ChartType.PIE, {"comparison_field": "cuve"}),
    "Tendance quotidienne du fuel": (ChartType.LINE, {"time_grouping": "day"}),
    "Consommation totale de fuel en 2025": (ChartType.NONE, {}),
}

if __name__ == "__main__":
    print("=" * 80)
    print("TEMPORAL DETECTION EXAMPLES")
    print("=" * 80)
    
    for question, expected in DETECTION_EXAMPLES.items():
        chart_type, metadata = detect_chart_type(question)
        expected_type, expected_meta = expected
        
        match = "✅" if chart_type == expected_type else "❌"
        print(f"\n{match} Question: {question}")
        print(f"   → Chart Type: {chart_type.value}")
        print(f"   → Metadata: {metadata}")
