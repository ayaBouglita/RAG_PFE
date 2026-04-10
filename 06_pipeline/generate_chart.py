"""
Génère les données structurées pour les graphiques (format Chart.js compatible)
"""

from typing import List, Dict, Any
from datetime import datetime
import json

class ChartDataBuilder:
    """Construit les structures de données pour les graphiques"""
    
    @staticmethod
    def build_line_chart(
        data: List[Dict],
        x_field: str,
        y_fields: List[str],
        title: str = "",
        unit: str = ""
    ) -> Dict[str, Any]:
        """
        Construit un graphique en ligne (évolution temporelle).
        
        Args:
            data: Données brutes (résultat SQL)
            x_field: Champ pour l'axe X (date, jour, mois, etc.)
            y_fields: Liste des champs à afficher en Y
            title: Titre du graphique
            unit: Unité des données (tonne, kWh, etc.)
        """
        
        if not data:
            return {"type": "line", "data": None, "error": "No data available"}
        
        # Trier par date
        sorted_data = sorted(data, key=lambda x: str(x.get(x_field, "")))
        
        labels = [str(row.get(x_field, "")) for row in sorted_data]
        
        datasets = []
        colors = [
            "rgb(0, 110, 195)",      # Primary blue
            "rgb(18, 35, 158)",      # Dark blue
            "rgb(127, 191, 42)",     # Green
            "rgb(76, 156, 218)",     # Light blue
            "rgb(139, 175, 206)",    # Steel blue
        ]
        
        for idx, y_field in enumerate(y_fields):
            values = [row.get(y_field) or 0 for row in sorted_data]
            
            datasets.append({
                "label": y_field,
                "data": values,
                "borderColor": colors[idx % len(colors)],
                "backgroundColor": colors[idx % len(colors)] + "20",  # Ajouter transparence
                "borderWidth": 2,
                "fill": True,
                "tension": 0.4,
                "pointRadius": 4,
                "pointHoverRadius": 6,
                "pointBackgroundColor": colors[idx % len(colors)]
            })
        
        # Calculer statistiques
        stats = {}
        for y_field in y_fields:
            values = [row.get(y_field) or 0 for row in sorted_data]
            stats[y_field] = {
                "total": sum(values),
                "moyenne": sum(values) / len(values) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
            }
        
        return {
            "type": "line",
            "title": title,
            "unit": unit,
            "data": {
                "labels": labels,
                "datasets": datasets
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {
                        "position": "top",
                    },
                    "title": {
                        "display": True,
                        "text": title
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {
                            "display": True,
                            "text": f"Montant ({unit})"
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": "Temps"
                        }
                    }
                }
            },
            "statistics": stats
        }
    
    @staticmethod
    def build_bar_chart(
        data: List[Dict],
        category_field: str,
        value_fields: List[str],
        title: str = "",
        unit: str = ""
    ) -> Dict[str, Any]:
        """Construit un graphique en barres (comparaisons)"""
        
        if not data:
            return {"type": "bar", "data": None, "error": "No data available"}
        
        # Trier par catégorie
        sorted_data = sorted(data, key=lambda x: str(x.get(category_field, "")))
        
        labels = [str(row.get(category_field, "")) for row in sorted_data]
        
        datasets = []
        colors = [
            "rgb(0, 110, 195)",
            "rgb(18, 35, 158)",
            "rgb(127, 191, 42)",
            "rgb(76, 156, 218)",
            "rgb(139, 175, 206)",
        ]
        
        for idx, value_field in enumerate(value_fields):
            values = [row.get(value_field) or 0 for row in sorted_data]
            
            datasets.append({
                "label": value_field,
                "data": values,
                "backgroundColor": colors[idx % len(colors)],
                "borderColor": colors[idx % len(colors)],
                "borderWidth": 1
            })
        
        # Calculer statistiques
        stats = {}
        for value_field in value_fields:
            values = [row.get(value_field) or 0 for row in sorted_data]
            stats[value_field] = {
                "total": sum(values),
                "moyenne": sum(values) / len(values) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
            }
        
        return {
            "type": "bar",
            "title": title,
            "unit": unit,
            "data": {
                "labels": labels,
                "datasets": datasets
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {
                        "position": "top",
                    },
                    "title": {
                        "display": True,
                        "text": title
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {
                            "display": True,
                            "text": f"Montant ({unit})"
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": category_field.replace("_", " ").capitalize()
                        }
                    }
                }
            },
            "statistics": stats
        }
    
    @staticmethod
    def build_pie_chart(
        data: List[Dict],
        category_field: str,
        value_field: str,
        title: str = "",
        unit: str = ""
    ) -> Dict[str, Any]:
        """Construit un graphique en camembert (répartitions)"""
        
        if not data:
            return {"type": "pie", "data": None, "error": "No data available"}
        
        labels = [str(row.get(category_field, "")) for row in data]
        values = [row.get(value_field) or 0 for row in data]
        total = sum(values)
        
        colors = [
            "rgb(0, 110, 195)",
            "rgb(18, 35, 158)",
            "rgb(127, 191, 42)",
            "rgb(76, 156, 218)",
            "rgb(139, 175, 206)",
            "rgb(255, 159, 64)",
            "rgb(255, 99, 132)",
        ]
        
        return {
            "type": "pie",
            "title": title,
            "unit": unit,
            "data": {
                "labels": labels,
                "datasets": [{
                    "data": values,
                    "backgroundColor": [colors[i % len(colors)] for i in range(len(labels))],
                    "borderColor": "#fff",
                    "borderWidth": 2
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {
                        "position": "bottom",
                    },
                    "title": {
                        "display": True,
                        "text": title
                    },
                    "tooltip": {
                        "callbacks": {
                            "label": "function(context) { return context.label + ': ' + context.parsed + ' (' + (context.parsed/total*100).toFixed(1) + '%)'; }"
                        }
                    }
                }
            },
            "statistics": {
                "total": total,
                "average": total / len(values) if values else 0,
                "items": len(values)
            }
        }


# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple de données
    sample_data = [
        {"date": "2025-01-01", "consommation": 100, "equipement": "Eq1"},
        {"date": "2025-01-02", "consommation": 120, "equipement": "Eq1"},
        {"date": "2025-01-03", "consommation": 110, "equipement": "Eq1"},
    ]
    
    builder = ChartDataBuilder()
    
    # Test Line Chart
    line_chart = builder.build_line_chart(
        sample_data,
        x_field="date",
        y_fields=["consommation"],
        title="Évolution de la consommation",
        unit="tonne"
    )
    print("Line Chart:")
    print(json.dumps(line_chart, indent=2, ensure_ascii=False))
