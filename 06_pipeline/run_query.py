import pyodbc
import pandas as pd

from db_config import build_connection_string

#Fonction pour exécuter une requête SQL de type SELECT
#et retourner les résultats sous forme de DataFrame
def execute_select_query(sql: str) -> pd.DataFrame:
    conn_str = build_connection_string()

#Connexion à la base de données et exécution de la requête
    with pyodbc.connect(conn_str) as conn:
        df = pd.read_sql(sql, conn)
     
    return df

#Exemple d'utilisation de la fonction d'exécution de requête
if __name__ == "__main__":
    test_sql = "SELECT TOP 5 * FROM dbo.Fact_Fuel;"
    df = execute_select_query(test_sql)
    print(df)