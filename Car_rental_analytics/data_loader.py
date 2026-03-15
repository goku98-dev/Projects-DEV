import pandas as pd
from db_connection import get_connection

def load_table(table_name):
    conn = get_connection()
    query = f"SELECT * FROM public.{table_name};"
    df = pd.read_sql(query, conn)
    conn.close()
    return df
