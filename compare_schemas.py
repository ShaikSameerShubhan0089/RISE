import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')

MYSQL_URL = "mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss"
POSTGRES_URL = os.getenv("DATABASE_URL")

def compare():
    ms_engine = create_engine(MYSQL_URL)
    pg_engine = create_engine(POSTGRES_URL)
    
    ms_insp = inspect(ms_engine)
    pg_insp = inspect(pg_engine)
    
    tables = ms_insp.get_table_names()
    
    for table in tables:
        print(f"\n--- Table: {table} ---")
        ms_cols = {c['name']: str(c['type']) for c in ms_insp.get_columns(table)}
        
        if table not in pg_insp.get_table_names():
            print(f"!!! Table {table} MISSING in PostgreSQL")
            continue
            
        pg_cols = {c['name']: str(c['type']) for c in pg_insp.get_columns(table)}
        
        # Check for missing in PG
        missing_in_pg = [c for c in ms_cols if c not in pg_cols]
        if missing_in_pg:
            print(f"  Missing in PG: {missing_in_pg}")
            
        # Check for types
        for c in ms_cols:
            if c in pg_cols:
                if ms_cols[c] != pg_cols[c]:
                    # Shorten names for easier reading
                    ms_t = ms_cols[c].split('(')[0]
                    pg_t = pg_cols[c].split('(')[0]
                    if ms_t != pg_t:
                        print(f"  Type mismatch [{c}]: MySQL={ms_t} vs PG={pg_t}")

if __name__ == "__main__":
    compare()
