"""
Génère des requêtes SQL optimisées pour les analyses temporelles et comparatives
"""

from typing import Optional

class TemporalSQLBuilder:
    """Construit des requêtes SQL pour les analyses temporelles"""
    
    @staticmethod
    def build_temporal_fuel_query(
        time_grouping: str,
        year: int = 2025,
        metric: str = "SUM(f.Consommation_en_Tonne)"
    ) -> str:
        """
        Génère une requête SQL pour l'évolution du fuel sur une période.
        
        Args:
            time_grouping: "day", "week", "month", "quarter", "year"
            year: Année pour le filtre
            metric: Métrique à calculer (SUM, AVG, etc.)
        """
        
        if time_grouping == "day":
            sql = f"""
            SELECT 
                CAST(d.date_complete AS DATE) AS date_label,
                {metric} AS consommation
            FROM dbo.Fact_Fuel f
            JOIN dbo.DIM_DATE d ON f.id_date = d.id_date
            WHERE d.annee = {year}
            GROUP BY CAST(d.date_complete AS DATE)
            ORDER BY date_label;
            """
        
        elif time_grouping == "week":
            sql = f"""
            SELECT 
                DATEPART(WEEK, d.date_complete) AS week_label,
                DATEPART(YEAR, d.date_complete) AS year_label,
                {metric} AS consommation
            FROM dbo.Fact_Fuel f
            JOIN dbo.DIM_DATE d ON f.id_date = d.id_date
            WHERE d.annee = {year}
            GROUP BY DATEPART(YEAR, d.date_complete), DATEPART(WEEK, d.date_complete)
            ORDER BY year_label, week_label;
            """
        
        elif time_grouping == "month":
            sql = f"""
            SELECT 
                DATEPART(MONTH, d.date_complete) AS month_label,
                DATEPART(YEAR, d.date_complete) AS year_label,
                {metric} AS consommation
            FROM dbo.Fact_Fuel f
            JOIN dbo.DIM_DATE d ON f.id_date = d.id_date
            WHERE d.annee = {year}
            GROUP BY DATEPART(YEAR, d.date_complete), DATEPART(MONTH, d.date_complete)
            ORDER BY year_label, month_label;
            """
        
        elif time_grouping == "quarter":
            sql = f"""
            SELECT 
                DATEPART(QUARTER, d.date_complete) AS quarter_label,
                DATEPART(YEAR, d.date_complete) AS year_label,
                {metric} AS consommation
            FROM dbo.Fact_Fuel f
            JOIN dbo.DIM_DATE d ON f.id_date = d.id_date
            WHERE d.annee = {year}
            GROUP BY DATEPART(YEAR, d.date_complete), DATEPART(QUARTER, d.date_complete)
            ORDER BY year_label, quarter_label;
            """
        
        else:  # year
            sql = f"""
            SELECT 
                DATEPART(YEAR, d.date_complete) AS year_label,
                {metric} AS consommation
            FROM dbo.Fact_Fuel f
            JOIN dbo.DIM_DATE d ON f.id_date = d.id_date
            WHERE d.annee = {year}
            GROUP BY DATEPART(YEAR, d.date_complete)
            ORDER BY year_label;
            """
        
        return sql.strip()
    
    @staticmethod
    def build_temporal_electricity_query(
        time_grouping: str,
        year: int = 2025,
        metric: str = "SUM(e.Consommation_kWh)"
    ) -> str:
        """Génère une requête SQL pour l'évolution de l'électricité"""
        
        if time_grouping == "day":
            sql = f"""
            SELECT 
                CAST(d.date_complete AS DATE) AS date_label,
                {metric} AS consommation
            FROM dbo.Fact_Electricite e
            JOIN dbo.DIM_DATE d ON e.id_date = d.id_date
            WHERE d.annee = {year}
            GROUP BY CAST(d.date_complete AS DATE)
            ORDER BY date_label;
            """
        
        elif time_grouping == "week":
            sql = f"""
            SELECT 
                DATEPART(WEEK, d.date_complete) AS week_label,
                DATEPART(YEAR, d.date_complete) AS year_label,
                {metric} AS consommation
            FROM dbo.Fact_Electricite e
            JOIN dbo.DIM_DATE d ON e.id_date = d.id_date
            WHERE d.annee = {year}
            GROUP BY DATEPART(YEAR, d.date_complete), DATEPART(WEEK, d.date_complete)
            ORDER BY year_label, week_label;
            """
        
        elif time_grouping == "month":
            sql = f"""
            SELECT 
                DATEPART(MONTH, d.date_complete) AS month_label,
                DATEPART(YEAR, d.date_complete) AS year_label,
                {metric} AS consommation
            FROM dbo.Fact_Electricite e
            JOIN dbo.DIM_DATE d ON e.id_date = d.id_date
            WHERE d.annee = {year}
            GROUP BY DATEPART(YEAR, d.date_complete), DATEPART(MONTH, d.date_complete)
            ORDER BY year_label, month_label;
            """
        
        elif time_grouping == "quarter":
            sql = f"""
            SELECT 
                DATEPART(QUARTER, d.date_complete) AS quarter_label,
                DATEPART(YEAR, d.date_complete) AS year_label,
                {metric} AS consommation
            FROM dbo.Fact_Electricite e
            JOIN dbo.DIM_DATE d ON e.id_date = d.id_date
            WHERE d.annee = {year}
            GROUP BY DATEPART(YEAR, d.date_complete), DATEPART(QUARTER, d.date_complete)
            ORDER BY year_label, quarter_label;
            """
        
        else:  # year
            sql = f"""
            SELECT 
                DATEPART(YEAR, d.date_complete) AS year_label,
                {metric} AS consommation
            FROM dbo.Fact_Electricite e
            JOIN dbo.DIM_DATE d ON e.id_date = d.id_date
            WHERE d.annee = {year}
            GROUP BY DATEPART(YEAR, d.date_complete)
            ORDER BY year_label;
            """
        
        return sql.strip()
    
    @staticmethod
    def build_comparison_by_equipement(
        metric: str = "SUM(e.Consommation_kWh)",
        year: int = 2025
    ) -> str:
        """Génère une requête pour comparer par équipement"""
        
        sql = f"""
        SELECT 
            eq.nom_equipement AS equipement,
            {metric} AS consommation
        FROM dbo.Fact_Electricite e
        JOIN dbo.DIM_DATE d ON e.id_date = d.id_date
        JOIN dbo.Dim_equipement eq ON e.id_equipement = eq.id_equipement
        WHERE d.annee = {year}
        GROUP BY eq.nom_equipement
        ORDER BY consommation DESC;
        """
        
        return sql.strip()
    
    @staticmethod
    def build_comparison_by_cuve(
        metric: str = "SUM(f.Consommation_en_Tonne)",
        year: int = 2025
    ) -> str:
        """Génère une requête pour comparer par cuve"""
        
        sql = f"""
        SELECT 
            c.nom_cuve AS cuve,
            {metric} AS consommation
        FROM dbo.Fact_Fuel f
        JOIN dbo.DIM_DATE d ON f.id_date = d.id_date
        JOIN dbo.Dim_Cuve c ON f.id_cuve = c.id_cuve
        WHERE d.annee = {year}
        GROUP BY c.nom_cuve
        ORDER BY consommation DESC;
        """
        
        return sql.strip()
    
    @staticmethod
    def build_repartition_by_type_fuel(
        year: int = 2025
    ) -> str:
        """Génère une requête pour la répartition par type de fuel"""
        
        sql = f"""
        SELECT 
            tf.nom_fuel AS type_fuel,
            SUM(f.Consommation_en_Tonne) AS consommation
        FROM dbo.Fact_Fuel f
        JOIN dbo.DIM_DATE d ON f.id_date = d.id_date
        JOIN dbo.Dim_Type_Fuel tf ON f.id_type_fuel = tf.id_type_fuel
        WHERE d.annee = {year}
        GROUP BY tf.nom_fuel
        ORDER BY consommation DESC;
        """
        
        return sql.strip()


# Exemples
if __name__ == "__main__":
    builder = TemporalSQLBuilder()
    
    print("="*80)
    print("TEMPORAL SQL BUILDER EXAMPLES")
    print("="*80)
    
    print("\n1. FUEL - Évolution mensuelle:")
    print(builder.build_temporal_fuel_query("month"))
    
    print("\n2. ELECTRICITY - Évolution quotidienne:")
    print(builder.build_temporal_electricity_query("day"))
    
    print("\n3. Comparaison par équipement:")
    print(builder.build_comparison_by_equipement())
    
    print("\n4. Répartition par type de fuel:")
    print(builder.build_repartition_by_type_fuel())
