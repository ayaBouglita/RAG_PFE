"""
Pipeline RAG + LLM + CHARTS
Génère: réponse textuelle + SQL + graphique JSON (optionnel)
"""

import json
from typing import Dict, Any, Optional
from detect_temporal import detect_chart_type, ChartType
from generate_temporal_sql import TemporalSQLBuilder
from generate_chart import ChartDataBuilder
from generate_sql_ollama import generate_sql, extract_sql_only
from run_query import execute_select_query
from ask_database import humanize_results
import pandas as pd

class RAGPipelineWithCharts:
    """Pipeline RAG + LLM + Graphiques"""
    
    def __init__(self):
        self.sql_builder = TemporalSQLBuilder()
        self.chart_builder = ChartDataBuilder()
    
    def process_question(self, question: str) -> Dict[str, Any]:
        """
        Traite une question utilisateur et retourne:
        - L'explication textuelle
        - La requête SQL
        - (Optionnel) Configuration de graphique JSON
        """
        
        result = {
            "question": question,
            "sql_query": None,
            "response": None,
            "chart_config": None,
            "metadata": {}
        }
        
        # ÉTAPE 1: Détecter si un graphique est nécessaire
        print(f"\n[ÉTAPE 1] Détection temporelle...")
        chart_type, temporal_meta = detect_chart_type(question)
        result["metadata"]["chart_type"] = chart_type.value
        result["metadata"]["temporal"] = temporal_meta
        
        # ÉTAPE 2: Générer la requête SQL appropriée
        print(f"[ÉTAPE 2] Génération SQL (chart_type={chart_type.value})...")
        
        if chart_type == ChartType.NONE:
            # Question normale → SQL via LLM
            sql_result = generate_sql(question)
            sql_query = sql_result["sql"]
            is_text_response = sql_result.get("is_text_response", False)
        else:
            # Question temporelle → SQL optimisé
            sql_query = self._generate_optimized_sql(question, chart_type, temporal_meta)
            is_text_response = False
        
        result["sql_query"] = sql_query
        
        # ÉTAPE 3: Exécuter la requête SQL
        print(f"[ÉTAPE 3] Exécution SQL...")
        try:
            if is_text_response:
                response = sql_query  # Si c'est une réponse textuelle
                df_results = None
            else:
                df_results = execute_select_query(sql_query)
        except Exception as e:
            print(f"❌ Erreur SQL: {str(e)}")
            result["response"] = f"Erreur lors de l'exécution: {str(e)}"
            return result
        
        # ÉTAPE 4: Générer la réponse textuelle
        print(f"[ÉTAPE 4] Humanisation de la réponse...")
        if is_text_response:
            result["response"] = response
        elif df_results is not None and not df_results.empty:
            columns = list(df_results.columns)
            results_list = df_results.where(pd.notna(df_results), None).to_dict('records')
            humanized = humanize_results(question, sql_query, results_list, columns)
            # Assurer que la réponse n'est pas vide
            result["response"] = humanized if humanized and humanized.strip() else f"Résultats trouvés: {len(results_list)} enregistrement(s)"
        else:
            result["response"] = "Aucun résultat trouvé"
        
        # ÉTAPE 5: Générer le graphique (si nécessaire)
        if chart_type != ChartType.NONE and df_results is not None and not df_results.empty:
            print(f"[ÉTAPE 5] Génération du graphique ({chart_type.value})...")
            chart_config = self._generate_chart(
                chart_type,
                df_results,
                temporal_meta,
                question
            )
            result["chart_config"] = chart_config
        
        return result
    
    def _generate_optimized_sql(
        self,
        question: str,
        chart_type: ChartType,
        metadata: Dict
    ) -> str:
        """Génère une requête SQL optimisée pour le type de graphique"""
        
        question_lower = question.lower()
        time_grouping = metadata.get("time_grouping", "month")
        comparison_field = metadata.get("comparison_field")
        resource_type = metadata.get("resource_type", "fuel")
        
        # ÉVOLUTION TEMPORELLE (LINE CHART)
        if chart_type == ChartType.LINE:
            if resource_type == "electricity":
                return self.sql_builder.build_temporal_electricity_query(time_grouping)
            else:
                # Par défaut: fuel
                return self.sql_builder.build_temporal_fuel_query(time_grouping)
        
        # COMPARAISON (BAR CHART)
        elif chart_type == ChartType.BAR:
            if comparison_field == "equipement":
                return self.sql_builder.build_comparison_by_equipement()
            elif comparison_field == "cuve":
                return self.sql_builder.build_comparison_by_cuve()
            else:
                return self.sql_builder.build_comparison_by_equipement()
        
        # RÉPARTITION (PIE CHART)
        elif chart_type == ChartType.PIE:
            if resource_type == "electricity":
                return self.sql_builder.build_comparison_by_equipement()
            else:
                return self.sql_builder.build_repartition_by_type_fuel()
        
        # Fallback
        return self.sql_builder.build_temporal_fuel_query("month")
    
    def _generate_chart(
        self,
        chart_type: ChartType,
        df_results: pd.DataFrame,
        metadata: Dict,
        question: str
    ) -> Dict[str, Any]:
        """Génère la configuration du graphique"""
        
        data = df_results.to_dict('records')
        
        # Identifier les colonnes
        columns = list(df_results.columns)
        numeric_cols = df_results.select_dtypes(include=['number']).columns.tolist()
        
        if chart_type == ChartType.LINE:
            # Premier colonne = temps, autres = métriques
            x_field = columns[0]
            y_fields = numeric_cols if numeric_cols else [columns[1]] if len(columns) > 1 else []
            title = metadata.get("chart_title", f"Évolution {x_field}")
            unit = "tonne" if "Consommation_en_Tonne" in columns else "kWh"
            
            return self.chart_builder.build_line_chart(
                data, x_field, y_fields, title, unit
            )
        
        elif chart_type == ChartType.BAR:
            # Premier colonne = catégorie, autres = métriques
            category_field = columns[0]
            value_fields = numeric_cols if numeric_cols else [columns[1]] if len(columns) > 1 else []
            title = metadata.get("chart_title", f"Comparaison par {category_field}")
            unit = "tonne" if "Consommation_en_Tonne" in str(columns) else "kWh"
            
            return self.chart_builder.build_bar_chart(
                data, category_field, value_fields, title, unit
            )
        
        elif chart_type == ChartType.PIE:
            # Premier colonne = catégorie, deuxième = valeur
            category_field = columns[0]
            value_field = columns[1] if len(columns) > 1 else numeric_cols[0] if numeric_cols else None
            title = metadata.get("chart_title", "Répartition")
            unit = "tonne" if "Consommation_en_Tonne" in str(columns) else "kWh"
            
            if value_field:
                return self.chart_builder.build_pie_chart(
                    data, category_field, value_field, title, unit
                )
        
        return None


# EXEMPLE D'UTILISATION
if __name__ == "__main__":
    pipeline = RAGPipelineWithCharts()
    
    questions = [
        "Quelle est l'évolution de la consommation de fuel par mois en 2025?",
        "Consommation d'électricité pour chaque équipement?",
        "Répartition de la consommation par type de fuel",
        "Consommation totale de fuel en 2025"
    ]
    
    for question in questions:
        print("\n" + "="*80)
        print(f"QUESTION: {question}")
        print("="*80)
        
        result = pipeline.process_question(question)
        
        print(f"\n✅ SQL Query:\n{result['sql_query']}")
        print(f"\n✅ Response:\n{result['response']}")
        
        if result['chart_config']:
            print(f"\n📊 Chart Type: {result['chart_config']['type']}")
            print(f"   Title: {result['chart_config']['title']}")
            print(f"   Labels: {result['chart_config']['data']['labels'][:3]}...")
        else:
            print("\n📊 No chart")
