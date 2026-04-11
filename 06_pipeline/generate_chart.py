"""
Génère les données structurées pour les graphiques (format Chart.js compatible)
"""

from typing import List, Dict, Any
from datetime import datetime
import json

class ChartDataBuilder:
    """Construit les structures de données pour les graphiques"""
    
    # Dictionnaire de traductions français pour les labels
    LABEL_TRANSLATIONS = {
        # Labels français
        "consommation": "Consommation",
        "consommation_en_tonne": "Consommation (Tonne)",
        "consommation_kwh": "Consommation (kWh)",
        "month_label": "Mois",
        "year_label": "Année",
        "day_label": "Jour",
        "week_label": "Semaine",
        "quarter_label": "Trimestre",
        "equipement": "Équipement",
        "cuve": "Cuve",
        "type_fuel": "Type de Fuel",
        "etat": "État",
        "equipe": "Équipe",
        # Labels anglais non traduits (de la base de données)
        "month_label": "Mois",
        "year_label": "Année",
        "day_label": "Jour",
        "week_label": "Semaine",
        "quarter_label": "Trimestre",
        "month": "Mois",
        "year": "Année",
        "day": "Jour",
        "week": "Semaine",
        "quarter": "Trimestre",
        "temps": "Temps",
        "montant": "Montant"
    }
    
    @staticmethod
    def translate_label(label: str) -> str:
        """Traduit un label en français"""
        label_lower = label.lower()
        return ChartDataBuilder.LABEL_TRANSLATIONS.get(label_lower, label)
    
    @staticmethod
    def identify_date_columns(columns: List[str]) -> tuple:
        """
        Identifie les colonnes de date et les colonnes de données.
        Retourne (date_columns, data_columns)
        """
        date_keywords = ['month_label', 'year_label', 'day_label', 'week_label', 
                        'quarter_label', 'date_label', 'annee', 'mois', 'jour', 'semaine']
        
        date_cols = []
        data_cols = []
        
        for col in columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in date_keywords):
                date_cols.append(col)
            else:
                data_cols.append(col)
        
        return date_cols, data_cols
    
    @staticmethod
    def build_x_label(row: Dict, date_cols: List[str]) -> str:
        """Construit un label d'axe X à partir des colonnes de date"""
        if not date_cols:
            return ""
        
        # Ordre de priorité pour les labels
        label_parts = []
        
        # Chercher le jour
        for col in date_cols:
            if 'day_label' in col.lower() or 'date_label' in col.lower():
                val = row.get(col)
                if val:
                    label_parts.insert(0, str(val))
                    break
        
        # Chercher la semaine
        for col in date_cols:
            if 'week_label' in col.lower():
                val = row.get(col)
                if val:
                    label_parts.append(f"S{val}")
                    break
        
        # Chercher le mois
        month_names = {1: 'Jan', 2: 'Fév', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Juin',
                      7: 'Juil', 8: 'Aoû', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Déc'}
        for col in date_cols:
            if 'month_label' in col.lower():
                val = row.get(col)
                if val:
                    month_str = month_names.get(int(val), str(val))
                    label_parts.append(month_str)
                    break
        
        # Chercher le trimestre
        for col in date_cols:
            if 'quarter_label' in col.lower():
                val = row.get(col)
                if val:
                    label_parts.append(f"T{val}")
                    break
        
        # Chercher l'année
        for col in date_cols:
            if 'year_label' in col.lower():
                val = row.get(col)
                if val:
                    label_parts.append(str(val))
                    break
        
        return " ".join(label_parts)
    
    @staticmethod
    def build_line_chart(
        data: List[Dict],
        x_field: str = None,
        y_fields: List[str] = None,
        title: str = "",
        unit: str = ""
    ) -> Dict[str, Any]:
        """
        Construit un graphique en ligne (évolution temporelle).
        
        Args:
            data: Données brutes (résultat SQL)
            x_field: IGNORÉ - identifié automatiquement
            y_fields: IGNORÉ - identifié automatiquement
            title: Titre du graphique
            unit: Unité des données (tonne, kWh, etc.)
        """
        
        if not data:
            return {"type": "line", "data": None, "error": "No data available"}
        
        # Identifier automatiquement les colonnes de date et données
        columns = list(data[0].keys())
        date_cols, data_cols = ChartDataBuilder.identify_date_columns(columns)
        
        # Si pas de colonnes de données trouvées, tout est donnée sauf la première date
        if not data_cols and date_cols:
            data_cols = [col for col in columns if col not in date_cols]
        
        # Fonction de tri personnalisée pour les dates
        def sort_key(row):
            """Trie par chronologie: year -> month -> week -> day -> quarter"""
            sort_vals = []
            
            # Cherche les colonnes de date dans l'ordre de priorité
            for date_col in date_cols:
                val = row.get(date_col)
                # Convertir en int pour un tri numérique
                try:
                    sort_vals.append(int(val) if val is not None else 0)
                except (ValueError, TypeError):
                    sort_vals.append(str(val) if val is not None else "")
            
            return tuple(sort_vals)
        
        # Trier les données par date
        sorted_data = sorted(data, key=sort_key)
        
        # Construire les labels de l'axe X à partir des colonnes de date
        labels = []
        for row in sorted_data:
            label = ChartDataBuilder.build_x_label(row, date_cols)
            labels.append(label if label else "N/A")
        
        datasets = []
        colors = [
            ("rgb(0, 110, 195)", "rgba(0, 110, 195, 0.15)"),      # Primary blue
            ("rgb(18, 35, 158)", "rgba(18, 35, 158, 0.15)"),      # Dark blue
            ("rgb(127, 191, 42)", "rgba(127, 191, 42, 0.15)"),     # Green
            ("rgb(76, 156, 218)", "rgba(76, 156, 218, 0.15)"),     # Light blue
            ("rgb(139, 175, 206)", "rgba(139, 175, 206, 0.15)"),   # Steel blue
        ]
        
        for idx, data_col in enumerate(data_cols):
            # Vérifier que c'est numérique avant d'ajouter
            sample = sorted_data[0].get(data_col) if sorted_data else None
            if not isinstance(sample, (int, float)):
                continue  # Sauter les colonnes non-numériques
            
            values = [row.get(data_col) or 0 for row in sorted_data]
            border_color, bg_color = colors[idx % len(colors)]
            
            datasets.append({
                "label": ChartDataBuilder.translate_label(data_col),
                "data": values,
                "borderColor": border_color,
                "backgroundColor": bg_color,
                "borderWidth": 2,
                "fill": True,
                "tension": 0.4,
                "pointRadius": 4,
                "pointHoverRadius": 6,
                "pointBackgroundColor": border_color
            })
        
        # Calculer statistiques - uniquement pour les colonnes numériques
        stats = {}
        for data_col in data_cols:
            sample = sorted_data[0].get(data_col) if sorted_data else None
            if isinstance(sample, (int, float)):
                values = [row.get(data_col) or 0 for row in sorted_data]
                stats[data_col] = {
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
                            "text": f"Consommation ({unit})",
                            "color": "rgb(18, 35, 158)"
                        },
                        "ticks": {
                            "color": "rgb(18, 35, 158)"
                        },
                        "grid": {
                            "color": "rgba(0, 110, 195, 0.1)"
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": "Date",
                            "color": "rgb(18, 35, 158)"
                        },
                        "ticks": {
                            "color": "rgb(18, 35, 158)"
                        },
                        "grid": {
                            "color": "rgba(0, 110, 195, 0.1)"
                        }
                    }
                }
            },
            "statistics": stats
        }
    
    @staticmethod
    def build_bar_chart(
        data: List[Dict],
        category_field: str = None,
        value_fields: List[str] = None,
        title: str = "",
        unit: str = ""
    ) -> Dict[str, Any]:
        """Construit un graphique en barres (comparaisons)"""
        
        if not data:
            return {"type": "bar", "data": None, "error": "No data available"}
        
        # Identifier automatiquement les colonnes de catégorie et données si non fournies
        columns = list(data[0].keys())
        date_cols, data_cols = ChartDataBuilder.identify_date_columns(columns)
        
        # Identifier la colonne de catégorie (première colonne non-date non-numérique)
        if not category_field:
            for col in columns:
                if col not in date_cols and not isinstance(data[0].get(col), (int, float)):
                    category_field = col
                    break
            # Si pas trouvée, utiliser la première colonne
            if not category_field:
                category_field = columns[0]
        
        # Identifier les colonnes de valeur (toutes les colonnes numériques sauf dates)
        if not value_fields:
            numeric_cols = []
            for col in columns:
                if col != category_field and col not in date_cols:
                    # Vérifier que c'est numérique
                    sample_val = data[0].get(col)
                    if isinstance(sample_val, (int, float)):
                        numeric_cols.append(col)
            value_fields = numeric_cols if numeric_cols else [col for col in columns if col != category_field and col not in date_cols]
        
        # Trier intelligemment: si colonnes de date existent, trier par date d'abord
        def sort_key_bar(row):
            """Trie par: colonnes de date numérique -> catégorie"""
            sort_vals = []
            
            # D'abord les colonnes de date (an, mois, semaine, etc.)
            for date_col in date_cols:
                val = row.get(date_col)
                try:
                    sort_vals.append(int(val) if val is not None else 0)
                except (ValueError, TypeError):
                    sort_vals.append(str(val) if val is not None else "")
            
            # Puis la catégorie
            cat_val = row.get(category_field, "")
            try:
                sort_vals.append(int(cat_val) if cat_val is not None else 0)
            except (ValueError, TypeError):
                sort_vals.append(str(cat_val) if cat_val is not None else "")
            
            return tuple(sort_vals)
        
        sorted_data = sorted(data, key=sort_key_bar)
        
        # Labels pour l'axe X
        labels = [ChartDataBuilder.translate_label(str(row.get(category_field, ""))) for row in sorted_data]
        
        datasets = []
        colors = [
            ("rgb(0, 110, 195)", "rgba(0, 110, 195, 0.2)"),      # Primary blue
            ("rgb(18, 35, 158)", "rgba(18, 35, 158, 0.2)"),      # Dark blue
            ("rgb(127, 191, 42)", "rgba(127, 191, 42, 0.2)"),     # Green
            ("rgb(76, 156, 218)", "rgba(76, 156, 218, 0.2)"),     # Light blue
            ("rgb(139, 175, 206)", "rgba(139, 175, 206, 0.2)"),   # Steel blue
        ]
        
        for idx, value_col in enumerate(value_fields):
            # Vérifier que c'est numérique avant d'ajouter
            sample = sorted_data[0].get(value_col) if sorted_data else None
            if not isinstance(sample, (int, float)):
                continue  # Sauter les colonnes non-numériques
            
            values = [row.get(value_col) or 0 for row in sorted_data]
            border_color, bg_color = colors[idx % len(colors)]
            
            datasets.append({
                "label": ChartDataBuilder.translate_label(value_col),
                "data": values,
                "backgroundColor": bg_color,
                "borderColor": border_color,
                "borderWidth": 1
            })
        
        # Calculer statistiques - uniquement pour les colonnes numériques
        stats = {}
        for value_col in value_fields:
            sample = sorted_data[0].get(value_col) if sorted_data else None
            if isinstance(sample, (int, float)):
                values = [row.get(value_col) or 0 for row in sorted_data]
                stats[value_col] = {
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
                            "text": f"Consommation ({unit})",
                            "color": "rgb(18, 35, 158)"
                        },
                        "ticks": {
                            "color": "rgb(18, 35, 158)"
                        },
                        "grid": {
                            "color": "rgba(0, 110, 195, 0.1)"
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": ChartDataBuilder.translate_label(category_field)
                        },
                        "ticks": {
                            "color": "rgb(18, 35, 158)"
                        },
                        "grid": {
                            "color": "rgba(0, 110, 195, 0.1)"
                        }
                    }
                }
            },
            "statistics": stats
        }
    
    @staticmethod
    def build_pie_chart(
        data: List[Dict],
        category_field: str = None,
        value_field: str = None,
        title: str = "",
        unit: str = ""
    ) -> Dict[str, Any]:
        """Construit un graphique en camembert (répartitions)"""
        
        if not data:
            return {
                "type": "pie",
                "title": title,
                "unit": unit,
                "data": {"labels": [], "datasets": [{"data": []}]},
                "options": {"responsive": True},
                "statistics": {}
            }
        
        # Identifier automatiquement les colonnes si non fournies
        columns = list(data[0].keys())
        date_cols, data_cols = ChartDataBuilder.identify_date_columns(columns)
        
        # La catégorie est la première colonne non-date non-numérique
        if not category_field:
            for col in columns:
                if col not in date_cols:
                    sample = data[0].get(col)
                    if not isinstance(sample, (int, float)):
                        category_field = col
                        break
        
        # La valeur est la première colonne numérique non-date
        if not value_field:
            # Chercher la première colonne numérique
            for col in columns:
                if col not in date_cols and col != category_field:
                    sample = data[0].get(col)
                    if isinstance(sample, (int, float)):
                        value_field = col
                        break
        
        if not category_field or not value_field:
            # Retourner un graphique vide au lieu de None
            return {
                "type": "pie",
                "title": title or "Répartition",
                "unit": unit,
                "data": {"labels": [], "datasets": [{"data": [], "backgroundColor": []}]},
                "options": {"responsive": True},
                "statistics": {}
            }
        
        # Vérifier que value_field est numérique
        sample_val = data[0].get(value_field)
        if not isinstance(sample_val, (int, float)):
            return {
                "type": "pie",
                "title": title or "Répartition",
                "unit": unit,
                "data": {"labels": [], "datasets": [{"data": [], "backgroundColor": []}]},
                "options": {"responsive": True},
                "statistics": {}
            }
        
        labels = [ChartDataBuilder.translate_label(str(row.get(category_field, ""))) for row in data]
        # Convertir à float pour s'assurer que c'est numérique
        values = [float(row.get(value_field) or 0) for row in data]
        total = sum(values) if values else 0
        
        colors_solid = [
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
                    "backgroundColor": [colors_solid[i % len(colors_solid)] for i in range(len(labels))],
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
                    }
                }
            },
            "statistics": {
                "total": {
                    "total": total,
                    "moyenne": total / len(values) if values else 0,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0
                }
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
