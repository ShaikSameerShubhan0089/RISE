import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')

MYSQL_URL = "mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss"
POSTGRES_URL = os.getenv("DATABASE_URL")

def get_counts(url, db_name):
    try:
        engine = create_engine(url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        counts = {}
        with engine.connect() as conn:
            for table in tables:
                try:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    counts[table] = count
                except:
                    counts[table] = "Error"
        return counts
    except Exception as e:
        return f"Error connecting to {db_name}: {e}"

print("Checking MySQL counts...")
mysql_counts = get_counts(MYSQL_URL, "MySQL")

print("\nChecking PostgreSQL counts...")
postgres_counts = get_counts(POSTGRES_URL, "PostgreSQL")

print("\nComparison:")
print(f"{'Table':<30} | {'MySQL':<10} | {'PostgreSQL':<10}")
print("-" * 60)

if isinstance(mysql_counts, dict) and isinstance(postgres_counts, dict):
    all_tables = sorted(set(list(mysql_counts.keys()) + list(postgres_counts.keys())))
    for table in all_tables:
        m = mysql_counts.get(table, "N/A")
        p = postgres_counts.get(table, "N/A")
        print(f"{table:<30} | {m:<10} | {p:<10}")
else:
    print(f"MySQL Error: {mysql_counts}")
    print(f"PostgreSQL Error: {postgres_counts}")
