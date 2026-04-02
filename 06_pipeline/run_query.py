import pyodbc
import pandas as pd

from db_config import build_connection_string


def execute_select_query(sql: str) -> pd.DataFrame:
    conn_str = build_connection_string()

    with pyodbc.connect(conn_str) as conn:
        df = pd.read_sql(sql, conn)

    return df


if __name__ == "__main__":
    test_sql = "SELECT TOP 5 * FROM dbo.Fact_Fuel;"
    df = execute_select_query(test_sql)
    print(df)