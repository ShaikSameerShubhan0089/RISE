import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')
url = os.getenv("DATABASE_URL")
engine = create_engine(url)
inspector = inspect(engine)
tables = inspector.get_table_names()

with open('full_schema_all.txt', 'w') as f:
    for table in tables:
        f.write(f"\n--- TABLE: {table} ---\n")
        columns = inspector.get_columns(table)
        for col in columns:
            f.write(f"{col['name']}: {col['type']}\n")

print("Schema written to full_schema_all.txt")
