import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')
MYSQL_URL = "mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss"
pg_engine = create_engine(os.getenv('DATABASE_URL'))
ms_engine = create_engine(MYSQL_URL)

ms_insp = inspect(ms_engine)
pg_insp = inspect(pg_engine)

tables = ms_insp.get_table_names()

for table in tables:
    print(f"\n--- Checking Table: {table} ---")
    ms_cols = {c['name'] for c in ms_insp.get_columns(table)}
    pg_cols = {c['name'] for c in pg_insp.get_columns(table)}
    
    missing = ms_cols - pg_cols
    extra = pg_cols - ms_cols
    
    if missing:
        print(f"  MISSING in PostgreSQL: {missing}")
    else:
        print("  All MySQL columns present in PostgreSQL.")
        
    if extra:
        print(f"  EXTRA in PostgreSQL: {extra}")
