import pyodbc

SERVER = '10.150.1.225'
DATABASE = 'PRD'
USERNAME = 'f.fareed'
PASSWORD = 'Faizaan@092419'
DRIVER = 'ODBC Driver 17 for SQL Server'

def get_connection():
    conn_str = (
        f"DRIVER={DRIVER};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD}"
    )
    return pyodbc.connect(conn_str)